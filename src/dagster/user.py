"""ETL-er Airflow user.

"""
import os
import logging
from typing import List

from dagster.utils import lazy

LAZY_AF_WWW_APP = lazy.Loader('airflow.www.app', globals(), 'airflow.www.app')
LAZY_AF_CLI = lazy.Loader('airflow.cli.simple_table', globals(), 'airflow.cli.simple_table')


def set_authentication():
    """Set the Airflow Admin/Superuser account.

    """
    airflow_user = os.environ.get('AF_USER', 'airflow')
    airflow_passwd = os.environ.get('AF_PASSWORD', 'airflow')

    delete_airflow_user(airflow_user)
    set_admin_user(airflow_user, airflow_passwd)
    list_airflow_users()


def set_admin_user(user: str, password: str):
    """Add Admin user to Airflow.

    """
    logging.info('Adding RBAC auth user "%s"', user)
    appbuilder = LAZY_AF_WWW_APP.cached_app().appbuilder # pylint: disable=no-member
    role = appbuilder.sm.find_role('Admin')
    fields = {
        'role': role,
        'username': user,
        'password': password,
        'email': str(),
        'first_name': 'Airflow',
        'last_name': 'Admin',
    }
    user = appbuilder.sm.add_user(**fields)
    if not user:
        logging.warning('Adding user "%s" failed', user)

    return user


def delete_airflow_user(user: str):
    """Remove user from RBAC.

    """
    logging.info('Deleting user "%s"', user)
    appbuilder = LAZY_AF_WWW_APP.cached_app().appbuilder # pylint: disable=no-member

    try:
        matched_user = next(u for u in appbuilder.sm.get_all_users() if u.username == user)
        appbuilder.sm.del_register_user(matched_user)
    except StopIteration:
        logging.warning('Deleting user "%s" failed', user)


def list_airflow_users() -> List[str]:
    """List Airflow users.

    """
    appbuilder = LAZY_AF_WWW_APP.cached_app().appbuilder # pylint: disable=no-member
    users = appbuilder.sm.get_all_users()
    #fields = ['id', 'username', 'email', 'first_name', 'last_name', 'roles']

    #AirflowConsole().print_as(data=users,
    #                          output='table',
    #                          mapper=lambda x: {f: x.__getattribute__(f) for f in fields})

    return [x.username for x in users]
