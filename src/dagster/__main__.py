"""Dagster CLI.

"""

from dataclasses import dataclass
from enum import Enum
import sys

import typer

import dagster.api


@dataclass
class PublicRole(str, Enum):
    """Airflow authentication methods."""

    ADMIN = "admin"
    PUBLIC = "public"


@dataclass
class Provider(str, Enum):
    """Authentication OAuth 2.0 providers."""

    GOOGLE = "google"
    AZURE = "azure"


app = typer.Typer(
    add_completion=False,
    help="Dagster workflow manager CLI tool",
)

config_app = typer.Typer(
    add_completion=False,
    help="Airflow webserver backend authentication config helper",
)
app.add_typer(config_app, name="config")

reset_app = typer.Typer(
    add_completion=False,
    help="Airflow webserver DAG reset helper",
)
app.add_typer(reset_app, name="reset")


@config_app.command("dbauth")
def config_dbauth(
    public_role: PublicRole = typer.Option(
        None, help="Auth role for Public access", show_default=False
    )
) -> None:
    """Airflow DB auth config generator."""
    mapping = {
        "authtype": "dbauth",
        "public_role": public_role,
    }
    auth_type(mapping)


@config_app.command("oauth")
def config_oauth(
    provider: Provider = typer.Option(
        None, help="OAuth 2.0 provider", show_default=False
    )
) -> None:
    """Airflow OAuth 2.0 provider generator."""
    mapping = {"authtype": "oauth", "provider": provider}
    auth_type(mapping)


@reset_app.command("bootstrap")
def bootstrap_reset() -> None:
    """Bootstrap DAG reset."""
    dagster.api.clear_bootstrap_dag()


def auth_type(mapping: dict) -> None:
    """Airflow webserver_config.py generator wrapper."""
    webserver_config = dagster.api.set_templated_webserver_config(mapping)
    if webserver_config is not None:
        sys.stdout.write(webserver_config)


def main() -> None:
    """Script entry point."""
    app()


if __name__ == "__main__":
    main()
