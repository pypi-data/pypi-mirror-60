"""Commands for getting information about datasets."""

import sys

from operator import itemgetter

import click

import pygments
import pygments.lexers
import pygments.formatters

import dtoolcore
from dtoolcore.compare import (
    diff_identifiers,
    diff_sizes,
    diff_content,
)

from dtool_cli.cli import (
    base_dataset_uri_argument,
    dataset_uri_argument,
    dataset_uri_validation,
    CONFIG_PATH,
)

from dtool_info.utils import sizeof_fmt, date_fmt

item_identifier_argument = click.argument("item_identifier")


@click.command()
@click.option(
    "-f",
    "--full",
    is_flag=True,
    help="Include file hash comparisons."
)
@dataset_uri_argument
@click.argument("reference_dataset_uri", callback=dataset_uri_validation)
def diff(full, dataset_uri, reference_dataset_uri):
    """Report the difference between two datasets.

    1. Checks that the identifiers are identicial
    2. Checks that the sizes are identical
    3. Checks that the hashes are identical, if the '--full' option is used

    If a differences is detected in step 1, steps 2 and 3 will not be carried
    out. Similarly if a difference is detected in step 2, step 3 will not be
    carried out.

    When checking that the hashes are identical the hashes for the first
    dataset are recalculated using the hashing algorithm of the reference
    dataset.
    """

    def echo_header(desc, ds_name, ref_ds_name, prop):
        click.secho("Different {}".format(desc), fg="red")
        click.secho("ID, {} in '{}', {} in '{}'".format(
            prop, ds_name, prop, ref_ds_name))

    def echo_diff(diff):
        for d in diff:
            line = "{}, {}, {}".format(d[0], d[1], d[2])
            click.secho(line)

    ds = dtoolcore.DataSet.from_uri(dataset_uri)
    ref_ds = dtoolcore.DataSet.from_uri(reference_dataset_uri)

    num_items = len(list(ref_ds.identifiers))

    ids_diff = diff_identifiers(ds, ref_ds)
    if len(ids_diff) > 0:
        echo_header("identifiers", ds.name, ref_ds.name, "present")
        echo_diff(ids_diff)
        sys.exit(1)

    with click.progressbar(length=num_items,
                           label="Comparing sizes") as progressbar:
        sizes_diff = diff_sizes(ds, ref_ds, progressbar)
    if len(sizes_diff) > 0:
        echo_header("sizes", ds.name, ref_ds.name, "size")
        echo_diff(sizes_diff)
        sys.exit(2)

    if full:
        with click.progressbar(length=num_items,
                               label="Comparing hashes") as progressbar:
            content_diff = diff_content(ds, ref_ds, progressbar)
        if len(content_diff) > 0:
            echo_header("content", ds.name, ref_ds.name, "hash")
            echo_diff(content_diff)
            sys.exit(3)


def _list_dataset_items(uri, quiet, verbose):
    try:
        dataset = dtoolcore.DataSet.from_uri(
            uri=uri,
            config_path=CONFIG_PATH
        )
    except dtoolcore.DtoolCoreTypeError:
        click.secho(
            "Cannot list the items of a proto dataset",
            fg="red",
            err=True
        )
        sys.exit(1)

    content = []
    for i in dataset.identifiers:
        props = dataset.item_properties(i)
        content.append({
            "identifier": i,
            "relpath": props["relpath"],
            "size_in_bytes": props["size_in_bytes"]
        })

    for c in sorted(content, key=itemgetter("relpath")):
        line = "{}\t{}".format(c["identifier"], c["relpath"])
        if verbose:
            line = "{}{}  {}".format(
                c["identifier"],
                sizeof_fmt(c["size_in_bytes"]),
                c["relpath"]
            )
        if quiet:
            line = c["relpath"]
        click.secho(line)


def _list_datasets(base_uri, quiet, verbose):
    base_uri = dtoolcore.utils.sanitise_uri(base_uri)
    StorageBroker = dtoolcore._get_storage_broker(base_uri, CONFIG_PATH)
    info = []
    for uri in StorageBroker.list_dataset_uris(base_uri, CONFIG_PATH):
        admin_metadata = dtoolcore._admin_metadata_from_uri(uri, CONFIG_PATH)
        fg = "green"
        name = admin_metadata["name"]
        if admin_metadata["type"] == "protodataset":
            fg = "red"
            name = "*" + name
        i = dict(
            name=name,
            uuid=admin_metadata["uuid"],
            creator=admin_metadata["creator_username"],
            uri=uri,
            fg=fg)
        if "frozen_at" in admin_metadata:
            i["date"] = date_fmt(admin_metadata["frozen_at"])
        info.append(i)

    if len(info) == 0:
        sys.exit(0)

    for i in info:
        if quiet:
            click.secho(i["uri"], fg=i["fg"])
            continue
        click.secho(i["name"], fg=i["fg"])
        click.secho("  " + i["uri"])
        if verbose:
            click.secho("  " + i["creator"], nl=False)
            if "date" in i:
                click.secho("  " + i["date"], nl=False)
            click.secho("  " + i["uuid"])


@click.command()
@click.option("-q", "--quiet", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
@click.argument("uri")
def ls(quiet, verbose, uri):
    """List datasets / items in a dataset.

    If the URI is a dataset the items in the dataset will be listed.
    It is not possible to list the items in a proto dataset.

    If the URI is a location containing datasets the datasets will be listed.
    Proto datasets are highlighted in red.
    """
    if dtoolcore._is_dataset(uri, CONFIG_PATH):
        _list_dataset_items(uri, quiet, verbose)
    else:
        _list_datasets(uri, quiet, verbose)


@click.command()
@dataset_uri_argument
def identifiers(dataset_uri):
    """List the item identifiers in the dataset."""
    dataset = dtoolcore.DataSet.from_uri(dataset_uri)
    for i in dataset.identifiers:
        click.secho(i)


@click.command()
@dataset_uri_argument
@click.option(
    "-f",
    "--format",
    type=click.Choice(["json"]),
    help="Select the output format."
)
def summary(dataset_uri, format):
    """Report summary information about a dataset."""
    dataset = dtoolcore.DataSet.from_uri(dataset_uri)
    creator_username = dataset._admin_metadata["creator_username"]
    frozen_at = dataset._admin_metadata["frozen_at"]
    num_items = len(dataset.identifiers)
    tot_size = sum([dataset.item_properties(i)["size_in_bytes"]
                    for i in dataset.identifiers])

    if format == "json":
        json_lines = [
            '{',
            '  "name": "{}",'.format(dataset.name),
            '  "uuid": "{}",'.format(dataset.uuid),
            '  "creator_username": "{}",'.format(creator_username),
            '  "number_of_items": {},'.format(num_items),
            '  "size_in_bytes": {},'.format(tot_size),
            '  "frozen_at": {}'.format(frozen_at),
            '}',
        ]
        formatted_json = "\n".join(json_lines)
        colorful_json = pygments.highlight(
            formatted_json,
            pygments.lexers.JsonLexer(),
            pygments.formatters.TerminalFormatter())
        click.secho(colorful_json, nl=False)

    else:
        info = [
            ("name", dataset.name),
            ("uuid", dataset.uuid),
            ("creator_username", creator_username),
            ("number_of_items", str(num_items)),
            ("size", sizeof_fmt(tot_size).strip()),
            ("frozen_at", date_fmt(frozen_at)),
        ]
        for key, value in info:
            click.secho("{}: ".format(key), nl=False)
            click.secho(value, fg="green")


@click.group()
def item():
    """
    Get information about an item in the dataset.
    """


@item.command()
@dataset_uri_argument
@item_identifier_argument
def properties(dataset_uri, item_identifier):
    """Report item properties."""
    dataset = dtoolcore.DataSet.from_uri(dataset_uri)
    try:
        props = dataset.item_properties(item_identifier)
    except KeyError:
        click.secho(
            "No such item in dataset: {}".format(item_identifier),
            fg="red",
            err=True
        )
        sys.exit(20)

    json_lines = [
        '{',
        '  "relpath": "{}",'.format(props["relpath"]),
        '  "size_in_bytes": {},'.format(props["size_in_bytes"]),
        '  "utc_timestamp": {},'.format(props["utc_timestamp"]),
        '  "hash": "{}"'.format(props["hash"]),
        '}',
    ]
    formatted_json = "\n".join(json_lines)
    colorful_json = pygments.highlight(
        formatted_json,
        pygments.lexers.JsonLexer(),
        pygments.formatters.TerminalFormatter())
    click.secho(colorful_json, nl=False)


@item.command()
@dataset_uri_argument
@item_identifier_argument
def fetch(dataset_uri, item_identifier):
    """Return abspath to file with item content.

    Fetches the file from remote storage if required.
    """
    dataset = dtoolcore.DataSet.from_uri(dataset_uri)
    click.secho(dataset.item_content_abspath(item_identifier))


@item.command()
@click.argument("overlay_name")
@dataset_uri_argument
@item_identifier_argument
def overlay(overlay_name, dataset_uri, item_identifier):
    """Return abspath to file with item content.

    Fetches the file from remote storage if required.
    """
    dataset = dtoolcore.DataSet.from_uri(dataset_uri)
    if overlay_name not in dataset.list_overlay_names():
        click.secho(
            "No such overlay in dataset: {}".format(overlay_name),
            fg="red",
            err=True
        )
        sys.exit(4)
    overlay = dataset.get_overlay(overlay_name)

    try:
        click.secho(str(overlay[item_identifier]))
    except KeyError:
        click.secho(
            "No such identifier in overlay: {}".format(item_identifier),
            fg="red",
            err=True
        )
        sys.exit(5)


@item.command()
@dataset_uri_argument
@item_identifier_argument
def relpath(dataset_uri, item_identifier):
    """Return relpath associated with the item.
    """
    dataset = dtoolcore.DataSet.from_uri(dataset_uri)
    try:
        props = dataset.item_properties(item_identifier)
    except KeyError:
        click.secho(
            "No such item in dataset: {}".format(item_identifier),
            fg="red",
            err=True
        )
        sys.exit(21)
    click.secho(props["relpath"])


@click.command()
@click.option(
    "-f",
    "--full",
    is_flag=True,
    help="Include file hash comparisons."
)
@dataset_uri_argument
def verify(full, dataset_uri):
    """Verify the integrity of a dataset.
    """
    dataset = dtoolcore.DataSet.from_uri(dataset_uri)
    all_okay = True

    # Generate identifiers and sizes quickly without the
    # hash calculation used when calling dataset.generate_manifest().
    generated_sizes = {}
    generated_relpaths = {}
    for handle in dataset._storage_broker.iter_item_handles():
        identifier = dtoolcore.utils.generate_identifier(handle)
        size = dataset._storage_broker.get_size_in_bytes(handle)
        relpath = dataset._storage_broker.get_relpath(handle)
        generated_sizes[identifier] = size
        generated_relpaths[identifier] = relpath

    generated_identifiers = set(generated_sizes.keys())
    manifest_identifiers = set(dataset.identifiers)

    for i in generated_identifiers.difference(manifest_identifiers):
        message = "Unknown item: {} {}".format(
            i,
            generated_relpaths[i]
        )
        click.secho(message, fg="red")
        all_okay = False

    for i in manifest_identifiers.difference(generated_identifiers):
        message = "Missing item: {} {}".format(
            i,
            dataset.item_properties(i)["relpath"]
        )
        click.secho(message, fg="red")
        all_okay = False

    for i in manifest_identifiers.intersection(generated_identifiers):
        generated_size = generated_sizes[i]
        manifest_size = dataset.item_properties(i)["size_in_bytes"]
        if generated_size != manifest_size:
            message = "Altered item size: {} {}".format(
                i,
                dataset.item_properties(i)["relpath"]
            )
            click.secho(message, fg="red")
            all_okay = False

    if full:
        generated_manifest = dataset.generate_manifest()
        for i in manifest_identifiers.intersection(generated_identifiers):
            generated_hash = generated_manifest["items"][i]["hash"]
            manifest_hash = dataset.item_properties(i)["hash"]
            if generated_hash != manifest_hash:
                message = "Altered item hash: {} {}".format(
                    i,
                    dataset.item_properties(i)["relpath"]
                )
                click.secho(message, fg="red")
                all_okay = False

    if not all_okay:
        sys.exit(1)
    else:
        click.secho("All good :)", fg="green")


@click.command()
@base_dataset_uri_argument
def status(dataset_uri):
    """Return dataset status (frozen or proto)."""
    try:
        dtoolcore.DataSet.from_uri(
            uri=dataset_uri,
            config_path=CONFIG_PATH
        )
        click.secho("frozen", fg="green")
    except dtoolcore.DtoolCoreTypeError:
        click.secho("proto", fg="red")


@click.command()
@base_dataset_uri_argument
def uri(dataset_uri):
    """Return full dataset URI.

    Can be useful when working with absolute and relative paths.
    """
    try:
        ds = dtoolcore.DataSet.from_uri(
            uri=dataset_uri,
            config_path=CONFIG_PATH
        )
    except dtoolcore.DtoolCoreTypeError:
        ds = dtoolcore.ProtoDataSet.from_uri(
            uri=dataset_uri,
            config_path=CONFIG_PATH
        )
    click.secho(ds.uri)


@click.command()
@dataset_uri_argument
def uuid(dataset_uri):
    """Return the UUID of the dataset."""
    dataset = dtoolcore.DataSet.from_uri(dataset_uri)
    click.secho(dataset.uuid)
