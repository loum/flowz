"""Unit test cases for `flowz.templater`.

"""

from pathlib import Path, PurePath
import filester

import flowz.templater  # type: ignore[import]

TEMPLATE_FILE_PATH = PurePath(Path(__file__).resolve().parents[1]).joinpath(
    "files", "templates"
)


def test_build_from_template_local(tmp_path: Path) -> None:
    """Build file from template: LOCAL environment."""
    # Given a mapping definition
    env_map = {"t": "X", "env": "LOCAL"}

    # and a template file
    templated_file = "task_variables.json"
    template_file = f"{templated_file}.j2"
    template_file_path = TEMPLATE_FILE_PATH.joinpath(template_file)
    filester.copy_file(str(template_file_path), str(tmp_path.joinpath(template_file)))

    # when I render the template
    flowz.templater.build_from_template(
        env_map, str(tmp_path.joinpath(template_file)), True
    )

    # then the output should match
    with open(str(tmp_path.joinpath(templated_file)), encoding="utf-8") as _fh:
        received = _fh.read()

    expected = """{
    "simple-task": {
        "condition": "X_LOCAL"
    },
    "complex-task": {
        "condition": "X_LOCAL",
        "params": {
            "one": "1",
            "two": "2"
        }
    }
}"""
    assert received == expected, "Template render for LOCAL error"


def test_build_from_template_dev(tmp_path: Path) -> None:
    """Build file from template: DEV environment."""
    # Given a mapping definition
    env_map = {"t": "d", "env": "DEV"}

    # and a template file
    templated_file = "task_variables.json"
    template_file = f"{templated_file}.j2"
    template_file_path = TEMPLATE_FILE_PATH.joinpath(template_file)
    filester.copy_file(str(template_file_path), str(tmp_path.joinpath(template_file)))

    # when render the template
    received = flowz.templater.build_from_template(
        env_map, str(tmp_path.joinpath(template_file)), False
    )

    # then the output should match
    expected = """{
    "simple-task": {
        "condition": "d_DEV"
    },
    "complex-task": {
        "condition": "d_DEV",
        "params": {
            "one": "1",
            "two": "2"
        }
    }
}"""
    assert received == expected, "Template render for DEV error"


def test_build_from_template_prod(tmp_path: Path) -> None:
    """Build file from template: PROD environment."""
    # Given a mapping definition
    env_map = {"t": "p", "env": "PRD"}

    # and a template file
    templated_file = "task_variables.json"
    template_file = f"{templated_file}.j2"
    template_file_path = TEMPLATE_FILE_PATH.joinpath(template_file)
    filester.copy_file(str(template_file_path), str(tmp_path.joinpath(template_file)))

    # when render the template
    received = flowz.templater.build_from_template(
        env_map, str(tmp_path.joinpath(template_file)), False
    )

    expected = """{
    "simple-task": {
        "condition": "p_PRD"
    },
    "complex-task": {
        "condition": "p_PRD",
        "params": {
            "one": "1",
            "two": "2"
        }
    }
}"""
    assert received == expected, "Template render for PRD error"


def test_build_from_missing_template(tmp_path: Path) -> None:
    """Build file from template that is not defined."""
    # Given a mapping definition
    env_map = {"t": "i", "env": "TEST"}

    # and a template file that does not exist
    templated_file = "task_variables.json"
    template_file = f"{templated_file}.j2"

    # when the system renders the template
    flowz.templater.build_from_template(
        env_map, str(tmp_path.joinpath(template_file)), True
    )

    # then no rendered output file should exist
    assert not tmp_path.joinpath(
        templated_file
    ).exists(), "Template render for DEV error"


def test_build_from_dag_template_local(tmp_path: Path) -> None:
    """Build DAG variable file from template: LOCAL environment."""
    # Given a mapping definition
    env_map = {"dry_run": "true", "env": "LOCAL"}

    # and a template file
    templated_file = "dag_variables.json"
    template_file = f"{templated_file}.j2"
    template_file_path = TEMPLATE_FILE_PATH.joinpath(template_file)
    filester.copy_file(str(template_file_path), str(tmp_path.joinpath(template_file)))

    # when render the template
    flowz.templater.build_from_template(
        env_map, str(tmp_path.joinpath(template_file)), True
    )

    # then the output should match
    with open(tmp_path.joinpath(templated_file), encoding="utf-8") as _fh:
        received = _fh.read()

    expected = """{
    "SUPA-DAG_LOCAL": {
        "dry": true,
        "max_active_tasks": 4
    }  
}"""
    assert received == expected, "DAG Template render for LOCAL error"


def test_build_from_dag_template_dev(tmp_path: Path) -> None:
    """Build DAG variable file from template: DEV environment."""
    # Given a mapping definition
    env_map = {"dry_run": "false", "env": "DEV"}

    # and a template file
    templated_file = "dag_variables.json"
    template_file = f"{templated_file}.j2"
    template_file_path = TEMPLATE_FILE_PATH.joinpath(template_file)
    filester.copy_file(str(template_file_path), str(tmp_path.joinpath(template_file)))

    # when render the template
    flowz.templater.build_from_template(
        env_map, str(tmp_path.joinpath(template_file)), True
    )

    # then the output should match
    with open(tmp_path.joinpath(templated_file), encoding="utf-8") as _fh:
        received = _fh.read()

    expected = """{
    "SUPA-DAG_DEV": {
        "dry": false,
        "max_active_tasks": 4
    }  
}"""
    assert received == expected, "DAG Template render for LOCAL error"
