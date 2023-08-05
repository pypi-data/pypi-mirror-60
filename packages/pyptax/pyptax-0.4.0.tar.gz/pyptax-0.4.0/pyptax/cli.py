import click

import pyptax
from pyptax.exceptions import ClientError
from pyptax.exceptions import DateFormatError
from pyptax.exceptions import UnavailableDataError

LOGO_CLI = (
    " /$$$$$$$            /$$$$$$$    /$$\n"
    "| $$__  $$          | $$__  $$  | $$\n"
    "| $$  \\ $$ /$$   /$$| $$  \\ $$ /$$$$$$    /$$$$$$  /$$   /$$\n"
    "| $$$$$$$/| $$  | $$| $$$$$$$/|_  $$_/   |____  $$|  $$ /$$/\n"
    "| $$____/ | $$  | $$| $$____/   | $$      /$$$$$$$ \\  $$$$/\n"
    "| $$      | $$  | $$| $$        | $$ /$$ /$$__  $$  >$$  $$\n"
    "| $$      |  $$$$$$$| $$        |  $$$$/|  $$$$$$$ /$$/\\  $$\n"
    "|__/       \\____  $$|__/         \\___/   \\_______/|__/  \\__/\n"
    "           /$$  | $$\n"
    "          |  $$$$$$/\n"
    "           \\______/\n"
)


@click.group(invoke_without_command=True)
@click.option("--version", "-v", is_flag=True, default=False)
@click.pass_context
def cli(ctx, version):
    """
        PyPtax Command Line Interface

        PyPtax is a Python library to retrieve information on Ptax rates.
    """
    if not ctx.invoked_subcommand and version:
        click.secho(pyptax.__version__)
        ctx.exit()

    elif not ctx.invoked_subcommand:
        click.secho(LOGO_CLI, fg="green")
        click.secho(ctx.get_help(), fg="green")
        ctx.exit()


@cli.command("close")
@click.option("--date", "-d", required=True, type=str)
def close(date):
    """
        Provides bid and ask rates for the requested date.
    """
    try:
        click.secho(str(pyptax.ptax.close(date).display()), fg="green")
    except (ClientError, DateFormatError, UnavailableDataError) as exc:
        click.secho(str(exc), fg="red")
