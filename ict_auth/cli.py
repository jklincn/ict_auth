# ict_auth/cli.py

import typer

from . import core
from ._version import __version__

app = typer.Typer(
    help="A command-line tool for ICT network authentication.",
    add_completion=False,
)


@app.command()
def enable() -> None:
    """
    Enable the persistent connection service.
    """

    pass


@app.command()
def disable() -> None:
    """
    Disable the persistent connection service.
    """
    pass


@app.command()
def logs() -> None:
    """
    Show the logs of the last login attempt.
    """
    pass


@app.command(hidden=True)
def test() -> None:
    core.test()


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context = typer.Option(None),
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version information and exit",
        is_eager=True,
    ),
):
    if version:
        typer.echo({__version__})
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        try:
            core.main()
        except KeyboardInterrupt:
            print()


def run():
    app()
