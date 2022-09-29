"""Unit test cases for :module:`dagster.utils.templater`.
"""
import os
import filester

import dagster.utils.templater


def test_build_from_template_dry(working_dir):
    """Build file from template: LOCAL environment.
    """
    # Given a mapping definition
    env_map = {'t': 'X', 'env': 'LOCAL'}

    # and a template file
    templated_file = 'task_variables.json'
    template_file = f'{templated_file}.j2'
    template_file_path = os.path.join('tests', 'files', 'templates', template_file)
    filester.copy_file(template_file_path, os.path.join(working_dir, template_file))

    # when render the template
    dagster.utils.templater.build_from_template(env_map,
                                                os.path.join(working_dir, template_file),
                                                True)

    # then the output should match
    with open(os.path.join(working_dir, templated_file), encoding='utf-8') as _fh:
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
    msg = 'Template render for LOCAL error'
    assert received == expected, msg


def test_build_from_template_dev(working_dir):
    """Build file from template: DEV environment.
    """
    # Given a mapping definition
    env_map = {'t': 'd', 'env': 'DEV'}

    # and a template file
    templated_file = 'task_variables.json'
    template_file = f'{templated_file}.j2'
    template_file_path = os.path.join('tests', 'files', 'templates', template_file)
    filester.copy_file(template_file_path, os.path.join(working_dir, template_file))

    # when render the template
    abs_template_file = os.path.join(working_dir, template_file)
    received = dagster.utils.templater.build_from_template(env_map, abs_template_file, False)

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
    msg = 'Template render for DEV error'
    assert received == expected, msg


def test_build_from_template_prod(working_dir):
    """Build file from template: PROD environment.
    """
    # Given a mapping definition
    env_map = {'t': 'p', 'env': 'PRD'}

    # and a template file
    templated_file = 'task_variables.json'
    template_file = f'{templated_file}.j2'
    template_file_path = os.path.join('tests', 'files', 'templates', template_file)
    filester.copy_file(template_file_path, os.path.join(working_dir, template_file))

    # when render the template
    abs_template_file = os.path.join(working_dir, template_file)
    received = dagster.utils.templater.build_from_template(env_map, abs_template_file, False)

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
    msg = 'Template render for PRD error'
    assert received == expected, msg


def test_build_from_missing_template(working_dir):
    """Build file from template that is not defined.
    """
    # Given a mapping definition
    env_map = {'t': 'i', 'env': 'TEST'}

    # and a template file that does not exist
    templated_file = 'task_variables.json'
    template_file = f'{templated_file}.j2'

    # when the system renders the template
    dagster.utils.templater.build_from_template(env_map,
                                              os.path.join(working_dir, template_file),
                                              True)

    # then no rendered output file should exist
    msg = 'Template render for DEV error'
    assert not os.path.exists(templated_file), msg


def test_build_from_dag_template_dry(working_dir):
    """Build DAG variable file from template: LOCAL environment.
    """
    # Given a mapping definition
    env_map = {'dry_run': 'true', 'env': 'LOCAL'}

    # and a template file
    templated_file = 'dag_variables.json'
    template_file = f'{templated_file}.j2'
    template_file_path = os.path.join('tests', 'files', 'templates', template_file)
    filester.copy_file(template_file_path, os.path.join(working_dir, template_file))

    # when render the template
    dagster.utils.templater.build_from_template(env_map,
                                                os.path.join(working_dir, template_file),
                                                True)

    # then the output should match
    with open(os.path.join(working_dir, templated_file), encoding='utf-8') as _fh:
        received = _fh.read()

    expected = """{
    "SUPA-DAG_LOCAL": {
        "dry": true,
        "max_active_tasks": 4
    }  
}"""
    msg = 'DAG Template render for LOCAL error'
    assert received == expected, msg


def test_build_from_dag_template_dev(working_dir):
    """Build DAG variable file from template: DEV environment.
    """
    # Given a mapping definition
    env_map = {'dry_run': 'false', 'env': 'DEV'}

    # and a template file
    templated_file = 'dag_variables.json'
    template_file = f'{templated_file}.j2'
    template_file_path = os.path.join('tests', 'files', 'templates', template_file)
    filester.copy_file(template_file_path, os.path.join(working_dir, template_file))

    # when render the template
    dagster.utils.templater.build_from_template(env_map,
                                                os.path.join(working_dir, template_file),
                                                True)

    # then the output should match
    with open(os.path.join(working_dir, templated_file), encoding='utf-8') as _fh:
        received = _fh.read()

    expected = """{
    "SUPA-DAG_DEV": {
        "dry": false,
        "max_active_tasks": 4
    }  
}"""
    msg = 'DAG Template render for LOCAL error'
    assert received == expected, msg
