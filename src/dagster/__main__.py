"""Dagster CLI.

"""
from typing import Text
import argparse
import sys

import dagster.api


DESCRIPTION = """Airflow Webserver helper"""


def main() -> None:
    """Script entry point."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    # Add sub-command support.
    subparsers = parser.add_subparsers(dest="command", help="command")

    # 'config' subcommand.
    config_help = "Airflow webserver config helper"
    config_parser = subparsers.add_parser("config", help=config_help)
    config_subparsers = config_parser.add_subparsers(dest="authtype")

    dbauth_parser = config_subparsers.add_parser("dbauth")
    public_role_help = "Auth role for Public access"
    dbauth_parser.add_argument(
        "-P",
        "--public-role",
        choices=["admin", "public"],
        default="admin",
        help=public_role_help,
    )

    oauth_parser = config_subparsers.add_parser("oauth")
    provider_help = "OAuth 2.0 provider"
    oauth_parser.add_argument(
        "-p", "--provider", choices=["google", "azure"], help=provider_help
    )

    dbauth_parser.set_defaults(func=dbauth_type)
    oauth_parser.set_defaults(func=oauth_type)

    # 'reset' subcommand.
    reset_help = "Airflow webserver DAG reset helper"
    reset_parser = subparsers.add_parser("reset", help=reset_help)
    reset_subparsers = reset_parser.add_subparsers(dest="dag")

    bootstrap_parser = reset_subparsers.add_parser("bootstrap")

    bootstrap_parser.set_defaults(func=reset_bootstrap)

    # Prepare the argument list.
    args = parser.parse_args()
    try:
        func = args.func
    except AttributeError:
        parser.print_help()
        parser.exit()
    func(args)


def dbauth_type(args: Text):
    """Airflow webserver_config.py dbauth flow."""
    mapping = {
        "authtype": args.authtype,
        "public_role": args.public_role,
    }
    auth_type(args, mapping)


def oauth_type(args):
    """Airflow webserver_config.py oauth flow."""
    mapping = {"authtype": args.authtype, "provider": args.provider}
    auth_type(args, mapping)


def auth_type(args, mapping):
    """Airflow webserver_config.py generator wrapper."""
    webserver_config = dagster.api.set_templated_webserver_config(mapping)
    sys.stdout.write(webserver_config)


def reset_bootstrap(args):
    """Airflow bootstrapper reset."""
    dagster.api.clear_bootstrap_dag()


if __name__ == "__main__":
    main()
