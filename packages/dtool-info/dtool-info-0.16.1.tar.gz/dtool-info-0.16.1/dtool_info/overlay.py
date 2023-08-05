"""Commands for displaying dataset overlay information."""

import json
import sys

import click

import pygments
import pygments.lexers
import pygments.formatters

import dtoolcore

from dtool_cli.cli import (
    dataset_uri_argument,
)


@click.group()
def overlay():
    """
    DEPRECATED: Get information about item metadata stored in overlays.
    """
    click.secho(
        "The ``dtool overlay`` command is deprecated",
        fg="red",
        err=True
    )
    click.secho(
        "Use ``dtool overlays`` instead",
        fg="red",
        err=True
    )


@overlay.command()
@dataset_uri_argument
def ls(dataset_uri):
    """
    DEPRECATED: List the overlays in the dataset.
    """
    dataset = dtoolcore.DataSet.from_uri(dataset_uri)
    for overlay_name in dataset.list_overlay_names():
        click.secho(overlay_name)


@overlay.command()
@dataset_uri_argument
@click.argument("overlay_name")
def show(dataset_uri, overlay_name):
    """
    DEPRECATED: Show the content of a specific overlay.
    """
    dataset = dtoolcore.DataSet.from_uri(dataset_uri)
    try:
        overlay = dataset.get_overlay(overlay_name)
    except:  # NOQA
        click.secho(
            "No such overlay: {}".format(overlay_name),
            fg="red",
            err=True
        )
        sys.exit(11)

    formatted_json = json.dumps(overlay, indent=2)
    colorful_json = pygments.highlight(
        formatted_json,
        pygments.lexers.JsonLexer(),
        pygments.formatters.TerminalFormatter())
    click.secho(colorful_json, nl=False)
