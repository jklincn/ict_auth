# ict_auth/cli.py
import logging
import os
import shlex
import sys
from pathlib import Path

import typer

from . import ci_test, core, systemd
from ._version import __version__
from .logger import configure_logging

app = typer.Typer(
    help="A command-line tool for ICT network authentication.",
    add_completion=False,
    pretty_exceptions_enable=False,
)

configure_logging("cli")
logger = logging.getLogger("ict_auth")
debug = os.getenv("DEBUG", "0")


@app.command()
def enable() -> None:
    """
    Enable the auto reconnection service.
    """
    account = core.ask_for_account()
    if debug == "1":
        account["debug"] = "1"
    systemd.create_service(
        service_name="ict_auth",
        executable_path=f"{shlex.quote(sys.executable)} -m ict_auth.service",
        description="ICT Network Authentication Service",
        restart_policy="always",
        RestartSec="10min",
        environment_vars=account,
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
        typer.echo(__version__)
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        core.main()


def run():
    app()
