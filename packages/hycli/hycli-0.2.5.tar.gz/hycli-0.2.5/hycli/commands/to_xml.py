import os

import click
from halo import Halo

from .. import convert_to_xml, Services


@click.command(context_settings=dict(max_content_width=200))
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "-e",
    "--endpoint-env",
    default="production",
    show_default=True,
    type=click.Choice(["localhost", "staging", "production"], case_sensitive=False),
    help="endpoint environment",
)
@click.option(
    "-u",
    "--username",
    envvar="HYCLI_API_USERNAME",
    help="your API username for staging",
)
@click.option(
    "-p",
    "--password",
    envvar="HYCLI_API_PASSWORD",
    help="your API username for staging",
)
@click.option(
    "-o",
    "--output",
    help="output directory for file",
    default=os.getcwd(),
    show_default=True,
    type=click.Path(exists=True),
)
def to_xml(path, endpoint_env, username, password, output):
    """ Convert invoice to xml """
    # Services available
    spinner = Halo(spinner="dots")
    spinner.start()
    services = Services(endpoint_env, username, password)
    spinner.succeed(f"Found file: {path}\n ")

    # Conversion
    convert_to_xml(
        path,
        output,
        services.extractor_endpoint,
        services.vat_validator_endpoint,
        services.validation_endpoint,
        services.token,
    )
    spinner.succeed("Converted invoice to xml")
