"""Flowz Airflow API.

"""

from pathlib import Path, PurePath
from typing import Iterator
import re

from dagsesh import lazy

from flowz.templater import build_from_template
from flowz.logging_config import log

LAZY_AF_CLI = lazy.Loader("airflow.cli", globals(), "airflow.cli")
LAZY_AF_MODELS = lazy.Loader("airflow.models", globals(), "airflow.models")
LAZY_AF_MODELS_DAG = lazy.Loader("airflow.models.dag", globals(), "airflow.models.dag")
LAZY_AF_CONF = lazy.Loader("airflow.configuration", globals(), "airflow.configuration")

DAGS_FOLDER = LAZY_AF_CONF.get("core", "DAGS_FOLDER")  # type: ignore[operator]


def set_templated_webserver_config(
    mapping: dict, path_to_config_template: str | None = None
) -> str | None:
    """Dynamically generate Airflow's `webserver_config.py` contents based on
    `mapping` settings.

    Function assumes a `webserver_config.py.j2` file exists under
    `path_to_config_template` directory.

    """
    if not path_to_config_template:
        path_to_config_template = str(
            PurePath(Path(__file__).resolve().parents[0]).joinpath(
                "config",
                "templates",
                "webserver",
            )
        )

    template_file = PurePath(Path(path_to_config_template)).joinpath(
        "webserver_config.py.j2"
    )
    rendered_content: str | None = build_from_template(
        mapping, str(template_file), write_output=False
    )

    return rendered_content


def list_dags(quiet: bool = False) -> Iterator[LAZY_AF_MODELS_DAG.DAG]:  # type: ignore
    """list the airflow.models.dag.DAG instances available in current context.

    Screen output can be suppressed by setting `quiet` to `True`.

    """
    dagbag = LAZY_AF_MODELS.DagBag(dag_folder=DAGS_FOLDER)  # type: ignore[operator]
    data = sorted(dagbag.dags.values(), key=lambda d: d.dag_id)

    if not quiet:
        LAZY_AF_CLI.simple_table.AirflowConsole().print_as(  # type: ignore
            data=sorted(dagbag.dags.values(), key=lambda d: d.dag_id),
            output="table",
            mapper=lambda x: {
                "dag_id": x.dag_id,
                "filepath": x.filepath,
                "owner": x.owner,
                "paused": x.get_is_paused(),
            },
        )

    yield from data


def filter_dags(token: str) -> list[LAZY_AF_MODELS_DAG.DAG]:  # type: ignore
    """Filter output of `flowz.list_dags` against `token`.

    Algorithm assumes a three-part DAG naming convention where each component is
    separated by an underscore (`_`). The second component is used for the `token` match.

    Returns the `airflow.models.dag.DAG` reference or `None` if not found.

    """
    matches = []
    prog = re.compile(token)
    for dag in list_dags(quiet=True):
        components = re.split("_", dag.dag_id)
        if len(components) >= 2:
            if prog.fullmatch(components[1]):
                matches.append(dag)

    return matches


def clear_bootstrap_dag() -> str | None:
    """Special DAG filter that clears the  bootstrapper DAG.

    Returns the name of the bootstrapper DAG that was cleared.

    """
    dag_id = None
    dags = filter_dags(token="BOOTSTRAP")
    if len(dags) > 1:
        log.error("Multiple BOOTSTRAP DAGs detected")
    elif dags:
        dag_id = dags[0].dag_id
        log.info('Clearing bootstrap DAG: "%s"', dag_id)
        LAZY_AF_MODELS_DAG.DAG.clear_dags(dags=[dags[0]])  # type: ignore

    return dag_id
