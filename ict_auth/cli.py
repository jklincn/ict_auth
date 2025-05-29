# ict_auth/cli.py

from pathlib import Path

import typer

from . import core, systemd, ci_test
from ._version import __version__
from .logger import logger

app = typer.Typer(
    help="""A command-line tool for ICT network authentication.

Run "ict_auth" without subcommands for login/logout.
""",
    add_completion=False,
)


@app.command()
def enable() -> None:
    """
    Enable the auto reconnection service.
    """
    # username, password = core.ask_for_account()
    systemd.create_service(
        service_name="ict_auth",
        executable_path=f"/usr/bin/python3 {Path(__file__).parent / 'service.py'}",
        description="ICT Network Authentication Service",
        restart_policy="always",
        RestartSec="10min",
    )
    systemd.restart_service("ict_auth")
    systemd.enable_service("ict_auth")
    logger.info("✅ Auto reconnection service enabled successfully.")


@app.command()
def disable() -> None:
    """
    Disable the auto reconnection service.
    """
    systemd.remove_service("ict_auth")
    logger.info("✅ Auto reconnection service disabled successfully.")


@app.command()
def logs() -> None:
    """
    Show the logs of auto reconnection service.
    """
    file = Path(__file__).parent / "ict_auth.log"
    if file.exists():
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                print(line, end="")
    else:
        logger.error("❌ Log file does not exist.")


@app.command(hidden=True)
def test() -> None:
    ci_test.test()


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
