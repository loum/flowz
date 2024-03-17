"""Unit test cases for :mod:`dagster.variable`.

"""

from pathlib import Path, PurePath
import pytest

from dagsesh import lazy

import dagster.variable  # type: ignore[import]

AF_UTILS = lazy.Loader("airflow.utils", globals(), "airflow.utils")
AF_MODELS = lazy.Loader("airflow.models", globals(), "airflow.models")
VARIABLES_PATH = PurePath(Path(__file__).resolve().parents[1]).joinpath(
    "files", "config", "tasks"
)
TASK_VARIABLE_COUNT = 10


@pytest.mark.parametrize("config_path", [VARIABLES_PATH])
def test_delete_task_variables(  # pylint: disable=unused-argument
    task_variables: int,
) -> None:
    """Test the pristine Airflow task Variables load."""
    # when I load in the configured Airflow task Variables

    # and attempt to delete a unknown key
    key = "banana"
    received = dagster.variable.del_variable_key(key)

    # then I should receive a False status
    assert not received, "Attempt to delete a unknown key should return False"

    # and I should receive the original count of Airflow Variables
    assert (
        task_variables == TASK_VARIABLE_COUNT
    ), "Variable list should not be empty (Airflow tasks)"


@pytest.mark.parametrize("config_path", [VARIABLES_PATH])
def test_pristine_load_of_task_variables(task_variables: int) -> None:
    """Test the pristine Airflow task Variables load."""
    # when I load in the configured Airflow task Variables

    # then I should receive a list of Airflow Variables
    assert (
        task_variables == TASK_VARIABLE_COUNT
    ), "Variable list should not be empty (Airflow tasks)"


@pytest.mark.parametrize("config_path", [VARIABLES_PATH])
def test_reload_of_task_variables(
    task_variables: int,  # pylint: disable=unused-argument
) -> None:
    """Test the reload of Airflow task Variables load."""
    # when I load in the configured Airflow task Variables

    # and then reload the configured Airflow task Variables
    received = dagster.variable.set_variables(str(VARIABLES_PATH))

    # then the load count should be 0
    assert not received, "Airflow task reload count should be 0"

    # and the Airflow task Variable count should remain unchanged
    with AF_UTILS.session.create_session() as session:  # type: ignore
        task_variable_count = (
            session.query(AF_MODELS.Variable.id)  # type: ignore
            .filter(~AF_MODELS.Variable.id.like("%_%_LOCAL"))  # type: ignore
            .count()
        )

    assert (
        task_variable_count == TASK_VARIABLE_COUNT
    ), "Variable list should not be empty (Airflow tasks)"


@pytest.mark.parametrize("config_path", [VARIABLES_PATH])
def test_reload_of_task_variables_missing_entry(  # pylint: disable=unused-argument
    task_variables: int,
) -> None:
    """Test the reload of Airflow task Variables load: missing entry."""
    # when I load in the configured Airflow task Variables

    # and delete an existing Airflow task Variable entry
    key = "task-01"
    dagster.variable.del_variable_key(key)

    # then the Airflow task Variable count should reduce by one
    with AF_UTILS.session.create_session() as session:  # type: ignore
        task_variable_count = (
            session.query(AF_MODELS.Variable.id)  # type: ignore
            .filter(~AF_MODELS.Variable.id.like("%_%_LOCAL"))  # type: ignore
            .count()
        )

    assert (
        task_variable_count == TASK_VARIABLE_COUNT - 1
    ), "Variable list should not be empty (Airflow tasks)"

    # and then when reload the configured Airflow task Variables
    received = dagster.variable.set_variables(str(VARIABLES_PATH))

    # then the load count should be 1
    assert received == 1, "Airflow task reload count should be 0"

    # and the original Airflow task Variable count should be restored
    with AF_UTILS.session.create_session() as session:  # type: ignore
        task_variable_count = (
            session.query(AF_MODELS.Variable.id)  # type: ignore
            .filter(~AF_MODELS.Variable.id.like("%_%_LOCAL"))  # type: ignore
            .count()
        )

    assert (
        task_variable_count == TASK_VARIABLE_COUNT
    ), "Restored Variable list should be restored (Airflow tasks)"


@pytest.mark.parametrize("config_path", [VARIABLES_PATH])
def test_get_variables(task_variables: int) -> None:  # pylint: disable=unused-argument
    """Test Airflow Variables get."""
    # when I load in the configured Airflow Variables

    # and I search for a known key
    key = "task-01"

    # then I should receive a match
    received = dagster.variable.get_variable(key)
    assert received, "Known variable expected to match from Airflow Variables DB"


@pytest.mark.parametrize("config_path", [VARIABLES_PATH])
def test_get_variables_unmatched(
    task_variables: int,  # pylint: disable=unused-argument
) -> None:
    """Test Airflow Variables get that is unmatched."""
    # when I load in the configured Airflow Variables

    # and I search for a unknown key
    key = "banana"

    # then I should not receive a match
    received = dagster.variable.get_variable(key)
    assert (
        not received
    ), "Unknown variable should not match against Airflow Variables DB"
