"""Unit test cases for :mod:`dagster.connection`.

"""

from __future__ import annotations
from typing import TYPE_CHECKING

import dagster.connection

if TYPE_CHECKING:
    from pathlib import PurePath


def test_set_logging_connection_remote_logging_not_defined(
    runtime_config_path: PurePath,
) -> None:
    """Test the logging connection: AIRFLOW__CORE__REMOTE_LOGGING not defined."""
    # Given a path to a templated connection
    connection_path = str(runtime_config_path.joinpath("logging", "sas"))

    # when the system tries to install a connection for the remote logging
    dagster.connection.set_logging_connection(connection_path)

    # and the "AIRFLOW__CORE__REMOTE_LOGGING" is not set

    # then no airflow.models.Connection should be created
    received = dagster.connection.list_connections()
    assert (
        received == []
    ), "Unset AIRFLOW__CORE__REMOTE_LOGGING should not create connections"
