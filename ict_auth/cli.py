# ict_auth/cli.py

import typer

from ict_auth import core

__version__ = "2.0.0"

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


@app.command()
def uninstall() -> None:
    """
    Uninstall the ict_auth package from the system.
    """
    pass


@app.callback(invoke_without_command=True)
def callback(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version information and exit",
        is_eager=True,
    ),
):
    if version:
        typer.echo(f"ict_auth {__version__}")
        raise typer.Exit()
    try:
        core.main()
    except KeyboardInterrupt:
        print()


def run():
    app()
