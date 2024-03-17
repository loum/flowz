"""Airflow connection helpers.

"""

from pathlib import Path, PurePath
import json

from dagsesh import lazy
from logga import log
from sqlalchemy.orm import exc
import filester

from dagster.templater import build_from_template

log.propagate = True

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

REMOTE_LOGGING = LAZY_AF_CONF.getboolean(  # type: ignore[operator]
    "logging", "REMOTE_LOGGING"
)


def set_connection(path_to_connections: str) -> None:
    """Add configuration items to Airflow `airflow.models.Connection`.

    Parameters:
        path_to_connections: File path the the Airflow connections configuration.

    """
    raw_connections = filester.get_directory_files(
        path_to_connections, file_filter="*.json"
    )
    log.info('Checking "%s" for Airflow connections ...', path_to_connections)
    for raw_connection in raw_connections:
        log.info('Found Airflow connection "%s"', raw_connection)
        with open(
            raw_connection,
            encoding="utf-8",
        ) as json_file:
            data = json.load(json_file)

            conn_extra = data.pop("conn_extra", None)
            new_conn = LAZY_AF_MODELS.Connection(**data)  # type: ignore[operator]
            if conn_extra:
                new_conn.set_extra(json.dumps(conn_extra))

            with LAZY_AF_UTILS.session.create_session() as session:  # type: ignore
                state = "OK"
                if (
                    session.query(LAZY_AF_MODELS.Connection)
                    .filter(
                        LAZY_AF_MODELS.Connection.conn_id == new_conn.conn_id  # type: ignore
                    )
                    .first()
                ):
                    state = "already exists"
                else:
                    session.add(new_conn)

                msg = f'Airflow connection "{data.get("conn_id")}" create status'
                log.info("%s: %s", msg, state)


def list_connections() -> list[str]:
    """Return connection information from Airflow connections table.

    Returns:
        list of all available connections.

    """
    with LAZY_AF_UTILS.session.create_session() as session:  # type: ignore[operator,attr-defined]
        query = session.query(LAZY_AF_MODELS.Connection)
        conns = query.all()

        LAZY_AF_CLI_SIMPLE_TABLE.AirflowConsole().print_as(  # type: ignore[operator]
            data=conns,
            output="table",
            mapper=LAZY_AF_CONNECTION_COMMAND._connection_mapper,  # pylint: disable=protected-access
        )

    return [x.conn_id for x in conns]


def delete_connection(key: str) -> None:
    """Delete connection `key` from DB.

    Parameters:
        key: The name of the Airflow Variable key.

    """
    log.info('Attempting to delete Airflow connection with conn_id: "%s"', key)
    with LAZY_AF_UTILS.session.create_session() as session:  # type: ignore[operator,attr-defined]
        try:
            to_delete = (
                session.query(LAZY_AF_MODELS.Connection)
                .filter(LAZY_AF_MODELS.Connection.conn_id == key)  # type: ignore[attr-defined]
                .one()
            )
        except exc.NoResultFound:
            log.warning('Did not find a connection with conn_id: "%s"', key)
        except exc.MultipleResultsFound:
            log.warning('Found more than one connection with conn_id: "%s"', key)
        else:
            session.delete(to_delete)
            log.info('Successfully deleted Airflow connection with conn_id: "%s"', key)


def set_templated_connection(
    path_to_connections: str, environment_override: str | None = None
) -> None:
    """Add configuration items to Airflow `airflow.models.Connection`.

    Connection templates are sourced from the `path_to_connections` directory and should feature
    a `*.j2` extension. Each template file should feature a single
    `airflow.models.Connection` definition in JSON format. For example:
    ```
        {
            "conn_id": "azure_wasb_logs",
            "conn_type": "wasb",
            "login": "login",
            "password": "secret"
        }
    ```

    Connections that are defined in the environment path override, `environment_override`, will
    task precedence over the defaults settings.

    Parameters:
        path_to_connections: File path the the Airflow connections configuration.
        environment_override: Provide an environment value that overrides settings defined
            under `path_to_connections`.

    """
    config_paths = []
    if environment_override is not None:
        config_paths.append(
            str(
                PurePath(Path(path_to_connections)).joinpath(
                    environment_override.lower()
                )
            )
        )
    config_paths.append(path_to_connections)

    for config_path in config_paths:
        for path_to_variable_template in filester.get_directory_files(
            str(config_path), file_filter="*.j2"
        ):
            rendered_content: str | None = build_from_template(
                {}, path_to_variable_template, write_output=False
            )
            if rendered_content is None:
                continue

            data = json.loads(rendered_content)

            conn_extra = data.pop("conn_extra", None)
            new_conn = LAZY_AF_MODELS.Connection(**data)  # type: ignore[operator]
            if conn_extra:
                new_conn.set_extra(json.dumps(conn_extra))

            with LAZY_AF_UTILS.session.create_session() as session:  # type: ignore[attr-defined]
                state = "OK"
                if (
                    session.query(LAZY_AF_MODELS.Connection)
                    .filter(
                        LAZY_AF_MODELS.Connection.conn_id == new_conn.conn_id  # type: ignore
                    )
                    .first()
                ):
                    state = "already exists"
                else:
                    session.add(new_conn)

                msg = f'Airflow connection "{data.get("conn_id")}" create status'
                log.info("%s: %s", msg, state)


def set_logging_connection(path_to_connections: str | None = None) -> None:
    """Logging configuration to Airflow `airflow.models.Connection`.

    Parameters:
        path_to_connections: Optional file path the the Airflow connections configuration.

    """
    if REMOTE_LOGGING:
        if not path_to_connections:
            path_to_connections = str(
                PurePath(Path(__file__).resolve().parents[0]).joinpath(
                    "config",
                    "templates",
                    "connections",
                    "logging",
                    "sas",
                )
            )
        set_templated_connection(path_to_connections)
    else:
        log.info('Remote logging not enabled. Check "AIRFLOW__LOGGING__REMOTE_LOGGING"')
