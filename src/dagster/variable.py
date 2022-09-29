"""Airflow Variable helpers.

"""
import os
import json
import logging
from typing import Any, Dict, Iterator
import filester

from dagster.utils import lazy
from dagster.utils.templater import build_from_template

LAZY_AF_UTILS = lazy.Loader('airflow.utils', globals(), 'airflow.utils')
LAZY_AF_MODELS = lazy.Loader('airflow.models', globals(), 'airflow.models')
LAZY_AF_CONF = lazy.Loader('airflow.configuration', globals(), 'airflow.configuration')

ENV_FILE = {
    'local': {'dry_run': 'true', 'env': 'LOCAL', 'alt_env': 'LOCAL'},
    'dev': {'dry_run': 'true', 'env': 'DEV', 'alt_env': 'DEV'},
    'prod': {'dry_run': 'false', 'env': 'PROD', 'alt_env': 'PROD'},
}
RUN_CONTEXT = os.environ.get('AIRFLOW_CUSTOM_ENV', 'LOCAL').lower()
DAGS_FOLDER = LAZY_AF_CONF.get('core', 'DAGS_FOLDER')


def set_variable(path_to_variables) -> int:
    """Add variable items to Airflow :class:`airflow.models.Variable`.

    Returns the number of variables inserted.

    """
    env_map = ENV_FILE.get(RUN_CONTEXT)

    counter = 0
    for path_to_variable_template in filester.get_directory_files(path_to_variables,
                                                                  file_filter='*.j2'):
        rendered_content = build_from_template(env_map, path_to_variable_template, False)

        data = json.loads(rendered_content)

        for var_name, values in data.items():
            if get_variable(var_name):
                logging.info('Inserting variable "%s" skipped: already exists', var_name)
            else:
                logging.info('Inserting variable "%s"', var_name)
                LAZY_AF_MODELS.Variable.set(var_name, json.dumps(values, indent=4))
                counter += 1

    return counter


def del_variable(path_to_variables: str):
    """Delete variable items from Airflow :class:`airflow.models.Variable`.

    """
    env_map = ENV_FILE.get(RUN_CONTEXT)

    for path_to_variable_template in filester.get_directory_files(path_to_variables,
                                                                  file_filter='*.j2'):
        rendered_content = build_from_template(env_map, path_to_variable_template, False)

        data = json.loads(rendered_content)

        for var_name in data.keys():
            del_variable_key(var_name)


def del_variable_key(key: str) -> bool:
    """Airflow Variable delete helper.

    """
    status = False
    logging.info('Deleting variable "%s"', key)
    status = LAZY_AF_MODELS.Variable.delete(key)
    if not status:
        logging.warning('Variable "%s" delete failed', key)

    return status == 1 or False


def list_variable() -> Iterator[Dict[str, Any]]:
    """List the variable items from Airflow :class:`airflow.models.Variable`.

    """
    with LAZY_AF_UTILS.session.create_session() as session:
        qry = session.query(LAZY_AF_MODELS.Variable).all()

        data = json.JSONDecoder()
        for var in qry:
            try:
                val = data.decode(var.val)
            except Exception:  # pylint: disable=broad-except
                val = var.val
            yield val


def get_variable(name: str) -> Dict[str, Any]:
    """Display variable by a given *name*.

    Returns the JSON value as a Python ``dict`` else None.

    """
    return LAZY_AF_MODELS.Variable.get(name, default_var=None, deserialize_json=True)
