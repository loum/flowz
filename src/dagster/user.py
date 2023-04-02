"""ETL-er Airflow user.

"""
from typing import List, Text
import logging
import os

from dagsesh import lazy

LAZY_AF_WWW_APP = lazy.Loader("airflow.www.app", globals(), "airflow.www.app")
LAZY_AF_CLI = lazy.Loader(
    "airflow.cli.simple_table", globals(), "airflow.cli.simple_table"
)


def set_authentication() -> None:
    """Set the Airflow Admin/Superuser account."""
    airflow_user = os.environ.get("AF_USER", "airflow")
    airflow_passwd = os.environ.get("AF_PASSWORD", "airflow")

    delete_airflow_user(airflow_user)
    set_admin_user(airflow_user, airflow_passwd)
    list_airflow_users()


def set_admin_user(user: Text, password: Text) -> Text:
    """Add Admin user to Airflow."""
    logging.info('Adding RBAC auth user "%s"', user)
    appbuilder = (
        LAZY_AF_WWW_APP.cached_app().appbuilder  # type: ignore  # pylint: disable=no-member
    )
    role = appbuilder.sm.find_role("Admin")
    fields = {
        "role": role,
        "username": user,
        "password": password,
        "email": "",
        "first_name": "Airflow",
        "last_name": "Admin",
    }
    user = appbuilder.sm.add_user(**fields)
    if not user:
        logging.warning('Adding user "%s" failed', user)

    return user


def delete_airflow_user(user: Text) -> None:
    """Remove user from RBAC."""
    logging.info('Deleting user "%s"', user)
    appbuilder = (
        LAZY_AF_WWW_APP.cached_app().appbuilder  # type: ignore  # pylint: disable=no-member
    )

    try:
        matched_user = next(
            u for u in appbuilder.sm.get_all_users() if u.username == user
        )
        appbuilder.sm.del_register_user(matched_user)
    except StopIteration:
        logging.warning('Deleting user "%s" failed', user)


def list_airflow_users() -> List[Text]:
    """List Airflow users."""
    appbuilder = (
        LAZY_AF_WWW_APP.cached_app().appbuilder  # type: ignore  # pylint: disable=no-member
    )
    users = appbuilder.sm.get_all_users()

    return [x.username for x in users]
