"""Unit test cases for :mod:`dagster.connection`.
"""
import os
import pathlib

import dagster.connection

CONNECTION_PATH = os.path.join(pathlib.Path(__file__).resolve().parents[2],
                               'src',
                               'dagster',
                               'config',
                               'templates',
                               'connections')


def test_set_logging_connection_remote_logging_not_defined():
    """Test the logging connection: AIRFLOW__CORE__REMOTE_LOGGING not defined.
    """
    # Given a path to a templated connection
    connection_path = os.path.join(CONNECTION_PATH, 'logging', 'sas')

    # when the system tries to install a connection for the remote logging
    dagster.connection.set_logging_connection(connection_path)

    # and the "AIRFLOW__CORE__REMOTE_LOGGING" is not set

    # then no airflow.models.Connection should be created
    received = dagster.connection.list_connections()
    msg = 'Unset AIRFLOW__CORE__REMOTE_LOGGING should not create connections'
    assert received == [], msg
