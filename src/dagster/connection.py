"""Airflow connection helpers.

"""
from typing import List, Optional, Text

import json
import logging
import os
import pathlib

from sqlalchemy.orm import exc
from dagsesh.utils import lazy
import filester

from dagster.templater import build_from_template

LAZY_AF_CONNECTION_COMMAND = lazy.Loader(
    "airflow.cli.commands.connection_command",
    globals(),
    "airflow.cli.commands.connection_command",
)
LAZY_AF_CLI_SIMPLE_TABLE = lazy.Loader(
    "airflow.cli.simple_table", globals(), "airflow.cli.simple_table"
)
LAZY_AF_UTILS = lazy.Loader("airflow.utils", globals(), "airflow.utils")
LAZY_AF_MODELS = lazy.Loader("airflow.models", globals(), "airflow.models")
LAZY_AF_CONF = lazy.Loader("airflow.configuration", globals(), "airflow.configuration")

REMOTE_LOGGING = LAZY_AF_CONF.getboolean("logging", "REMOTE_LOGGING")


def set_connection(path_to_connections: Text) -> None:
    """Add configuration items to Airflow `airflow.models.Connection`.

    Parameters:
        path_to_connections: File path the the Airflow connections configuration.

    """
    raw_connections = filester.get_directory_files(
        path_to_connections, file_filter="*.json"
    )
    logging.info('Checking "%s" for Airflow connections ...', path_to_connections)
    for raw_connection in raw_connections:
        logging.info('Found Airflow connection "%s"', raw_connection)
        with open(
            raw_connection,
            encoding="utf-8",
        ) as json_file:
            data = json.load(json_file)

            conn_extra = data.pop("conn_extra", None)
            new_conn = LAZY_AF_MODELS.Connection(**data)
            if conn_extra:
                new_conn.set_extra(json.dumps(conn_extra))

            with LAZY_AF_UTILS.session.create_session() as session:
                state = "OK"
                if (
                    session.query(LAZY_AF_MODELS.Connection)
                    .filter(LAZY_AF_MODELS.Connection.conn_id == new_conn.conn_id)
                    .first()
                ):
                    state = "already exists"
                else:
                    session.add(new_conn)

                msg = f'Airflow connection "{data.get("conn_id")}" create status'
                logging.info("%s: %s", msg, state)


def list_connections() -> List[Text]:
    """Return connection information from Airflow connections table.

    Returns:
        List of all available connections.

    """
    with LAZY_AF_UTILS.session.create_session() as session:
        query = session.query(LAZY_AF_MODELS.Connection)
        conns = query.all()

        LAZY_AF_CLI_SIMPLE_TABLE.AirflowConsole().print_as(
            data=conns,
            output="table",
            mapper=LAZY_AF_CONNECTION_COMMAND._connection_mapper,  # pylint: disable=protected-access
        )

    return [x.conn_id for x in conns]


def delete_connection(key: Text) -> None:
    """Delete connection `key` from DB.

    Parameters:
        key: The name of the Airflow Variable key.

    """
    logging.info('Attempting to delete Airflow connection with conn_id: "%s"', key)
    with LAZY_AF_UTILS.session.create_session() as session:
        try:
            to_delete = (
                session.query(LAZY_AF_MODELS.Connection)
                .filter(LAZY_AF_MODELS.Connection.conn_id == key)
                .one()
            )
        except exc.NoResultFound:
            logging.warning('Did not find a connection with conn_id: "%s"', key)
        except exc.MultipleResultsFound:
            logging.warning('Found more than one connection with conn_id: "%s"', key)
        else:
            session.delete(to_delete)
            logging.info(
                'Successfully deleted Airflow connection with conn_id: "%s"', key
            )


def set_templated_connection(path_to_connections: Text) -> None:
    """Add configuration items to Airflow `airflow.models.Connection`.

    Connection templates are sourced from the `path_to_connections` directory and should feature
    a `*.j2` extension.  Each template file should feature a single
    `airflow.models.Connection` definition in JSON format.  For example::

        {
            "conn_id": "azure_wasb_logs",
            "conn_type": "wasb",
            "login": "login",
            "password": "secret"
        }

    Parameters:
        path_to_connections: File path the the Airflow connections configuration.

    """
    for path_to_variable_template in filester.get_directory_files(
        path_to_connections, file_filter="*.j2"
    ):
        rendered_content = build_from_template({}, path_to_variable_template, False)

        data = json.loads(rendered_content)

        conn_extra = data.pop("conn_extra", None)
        new_conn = LAZY_AF_MODELS.Connection(**data)
        if conn_extra:
            new_conn.set_extra(json.dumps(conn_extra))

        with LAZY_AF_UTILS.session.create_session() as session:
            state = "OK"
            if (
                session.query(LAZY_AF_MODELS.Connection)
                .filter(LAZY_AF_MODELS.Connection.conn_id == new_conn.conn_id)
                .first()
            ):
                state = "already exists"
            else:
                session.add(new_conn)

            msg = f'Airflow connection "{data.get("conn_id")}" create status'
            logging.info("%s: %s", msg, state)


def set_logging_connection(path_to_connections: Optional[Text] = None) -> None:
    """Logging configuration to Airflow `airflow.models.Connection`.

    Parameters:
        path_to_connections: Optional file path the the Airflow connections configuration.

    """
    if REMOTE_LOGGING:
        if not path_to_connections:
            path_to_connections = os.path.join(
                pathlib.Path(__file__).resolve().parents[0],
                "config",
                "templates",
                "connections",
                "logging",
                "sas",
            )
        set_templated_connection(path_to_connections)
    else:
        logging.info(
            'Remote logging not enabled.  Check "AIRFLOW__LOGGING__REMOTE_LOGGING"'
        )
