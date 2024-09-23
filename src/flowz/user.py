"""Apache Airflow user account management.

"""

import os

from dagsesh import lazy
from logga import log

LAZY_AF_APP_BUILDER = lazy.Loader(
    "airflow.providers.fab.auth_manager.cli_commands.utils",
    globals(),
    "airflow.providers.fab.auth_manager.cli_commands.utils",
)
LAZY_AF_CLI = lazy.Loader(
    "airflow.cli.simple_table", globals(), "airflow.cli.simple_table"
)


def set_authentication() -> None:
    """Set the Airflow Admin/Superuser account."""
    airflow_user = os.environ.get("FLOWZ_AIRFLOW_ADMIN_USER", "airflow")
    airflow_passwd = os.environ.get("FLOWZ_AIRFLOW_ADMIN_PASSWORD", "airflow")

    delete_airflow_user(airflow_user)
    set_admin_user(airflow_user, airflow_passwd)
    list_airflow_users()


def set_admin_user(user: str, password: str) -> str:
    """Add Admin user to Airflow."""
    log.info('Adding RBAC auth user "%s"', user)

    with LAZY_AF_APP_BUILDER.get_application_builder() as appbuilder:  # type: ignore
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
        if user:
            log.info("Admin user bootstrapped successfully")
        else:
            log.warning('Adding user "%s" failed', user)

    return user


def delete_airflow_user(user: str) -> None:
    """Remove user from RBAC."""
    log.info('Deleting user "%s"', user)

    with LAZY_AF_APP_BUILDER.get_application_builder() as appbuilder:  # type: ignore
        try:
            matched_user = next(
                u for u in appbuilder.sm.get_all_users() if u.username == user
            )
            appbuilder.sm.del_register_user(matched_user)
        except StopIteration:
            log.warning(
                'Deleting user "%s" failed (ignore for pristine bootstrap)', user
            )


def list_airflow_users() -> list[str]:
    """List Airflow users."""
    users = []
    with LAZY_AF_APP_BUILDER.get_application_builder() as appbuilder:  # type: ignore
        users.extend(appbuilder.sm.get_all_users())

    return [x.username for x in users]
