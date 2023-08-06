import click
from halo import Halo

from .. import convert_to_xlsx, Services


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
@click.option("-w", "--workers", default=6, show_default=True, help="amount of workers")
def to_xlsx(path, endpoint_env, username, password, workers):
    """ Convert invoice to xlsx """
    # Services available
    spinner = Halo(spinner="dots")
    spinner.start()
    services = Services(endpoint_env, username, password)
    spinner.succeed(f"Found dir: {path}\n ")

    # Conversion
    convert_to_xlsx(path, services.token, services.extractor_endpoint, workers)
    spinner.succeed("Converted invoice(s) to xlsx")
