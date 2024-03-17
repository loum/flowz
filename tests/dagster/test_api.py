"""Unit test cases for `dagster.api`.

"""

from pathlib import Path, PurePath

import dagster.api

WEBSERVER_CONFIG_PATH = PurePath(Path(__file__).resolve().parents[1]).joinpath(
    "files", "webserver"
)


def test_set_templated_webserver_config_default_template() -> None:
    """Test the webserver_config.py create: "dbauth" auth and public role "Admin"."""
    # Given a mapping for the "dbauth" Airflow auth flow
    mapping = {
        "authtype": "dbauth",
        "public_role": "admin",
    }

    # when I generate the webserver_config.py file
    received = dagster.api.set_templated_webserver_config(mapping)

    # I should receive a valid webserver_config.py
    expected_path = WEBSERVER_CONFIG_PATH.joinpath(
        "dbauth",
        "admin",
        "webserver_config_py.out",
    )
    with open(str(expected_path), encoding="utf-8") as _fh:
        expected = _fh.read().splitlines()
    msg = (
        'LOCAL dev generated webserver_config.py with public role "Admin" content error'
    )
    assert received is not None and received.split("\n") == expected, msg


def test_set_templated_webserver_config(runtime_config_path: str) -> None:
    """Test the webserver_config.py create: "dbauth" auth and public role "Admin"."""
    # Given a mapping for the "dbauth" Airflow auth flow
    mapping = {
        "authtype": "dbauth",
        "public_role": "admin",
    }

    # when I generate the webserver_config.py file
    received = dagster.api.set_templated_webserver_config(
        mapping,
        str(PurePath(Path(runtime_config_path)).joinpath("templates", "webserver")),
    )

    # I should receive a valid webserver_config.py
    expected_path = WEBSERVER_CONFIG_PATH.joinpath(
        "dbauth",
        "admin",
        "webserver_config_py.out",
    )
    with open(str(expected_path), encoding="utf-8") as _fh:
        expected = _fh.read().splitlines()
    msg = (
        'LOCAL dev generated webserver_config.py with public role "Admin" content error'
    )
    assert received is not None and received.split("\n") == expected, msg


def test_set_templated_webserver_config_dbauth_with_public_role_as_public(
    runtime_config_path: str,
) -> None:
    """Test the webserver_config.py create: "dbauth" auth and public role "Public"."""
    # Given a mapping for the "dbauth" Airflow auth flow
    mapping = {
        "authtype": "dbauth",
        "public_role": "public",
    }

    # when I generate the webserver_config.py file
    received = dagster.api.set_templated_webserver_config(
        mapping,
        str(PurePath(Path(runtime_config_path)).joinpath("templates", "webserver")),
    )

    # I should receive a valid webserver_config.py
    expected_path = WEBSERVER_CONFIG_PATH.joinpath(
        "dbauth",
        "public",
        "webserver_config_py.out",
    )
    with open(str(expected_path), encoding="utf-8") as _fh:
        expected = _fh.read().splitlines()
    msg = 'LOCAL dev generated webserver_config.py with public role "Public" content error'
    assert received is not None and received.split("\n") == expected, msg


def test_set_templated_webserver_config_dbauth_with_no_public_role(
    runtime_config_path: str,
) -> None:
    """Test the webserver_config.py create: "dbauth" auth and no public role defined."""
    # Given a mapping for the "dbauth" Airflow auth flow
    mapping = {
        "authtype": "dbauth",
        "public_role": "public",
    }

    # when I generate the webserver_config.py file
    received = dagster.api.set_templated_webserver_config(
        mapping,
        str(PurePath(Path(runtime_config_path)).joinpath("templates", "webserver")),
    )

    # I should receive a valid webserver_config.py
    expected_path = WEBSERVER_CONFIG_PATH.joinpath(
        "dbauth",
        "public",
        "webserver_config_py.out",
    )
    with open(str(expected_path), encoding="utf-8") as _fh:
        expected = _fh.read().splitlines()
    msg = "LOCAL dev generated webserver_config.py with no public role content error"
    assert received is not None and received.split("\n") == expected, msg


def test_set_templated_webserver_config_oauth_flow(runtime_config_path: str) -> None:
    """Test the webserver_config.py create: OAuth 2.0 flow"""
    # Given a mapping for the K8s environment
    mapping = {"authtype": "oauth", "provider": None}

    # when I generate the webserver_config.py file
    received = dagster.api.set_templated_webserver_config(
        mapping,
        str(PurePath(Path(runtime_config_path)).joinpath("templates", "webserver")),
    )

    # I should receive a valid webserver_config.py
    expected_path = WEBSERVER_CONFIG_PATH.joinpath(
        "oauth",
        "webserver_config_py.out",
    )
    with open(str(expected_path), encoding="utf-8") as _fh:
        expected = _fh.read().splitlines()
    msg = "K8s generated webserver_config.py content error"
    assert received is not None and received.split("\n") == expected, msg


def test_set_templated_webserver_config_oauth_flow_provider_google(
    runtime_config_path: str,
) -> None:
    """Test the webserver_config.py create: OAuth 2.0 flow with Google as provider"""
    # Given a mapping for the K8s environment
    mapping = {"authtype": "oauth", "provider": "google"}

    # when I generate the webserver_config.py file
    received = dagster.api.set_templated_webserver_config(
        mapping,
        str(PurePath(Path(runtime_config_path)).joinpath("templates", "webserver")),
    )

    # I should receive a valid webserver_config.py
    expected_path = WEBSERVER_CONFIG_PATH.joinpath(
        "oauth",
        "google",
        "webserver_config_py.out",
    )
    with open(str(expected_path), encoding="utf-8") as _fh:
        expected = _fh.read().splitlines()
    msg = "K8s generated webserver_config.py content error"
    assert received is not None and received.split("\n") == expected, msg


def test_set_templated_webserver_config_oauth_flow_provider_azure(
    runtime_config_path: str,
) -> None:
    """Test the webserver_config.py create: OAuth 2.0 flow with Azure as provider"""
    # Given a mapping for the K8s environment
    mapping = {"authtype": "oauth", "provider": "azure"}

    # when I generate the webserver_config.py file
    received = dagster.api.set_templated_webserver_config(
        mapping,
        str(PurePath(Path(runtime_config_path)).joinpath("templates", "webserver")),
    )

    # I should receive a valid webserver_config.py
    expected_path = WEBSERVER_CONFIG_PATH.joinpath(
        "oauth",
        "azure",
        "webserver_config_py.out",
    )
    with open(str(expected_path), encoding="utf-8") as _fh:
        expected = _fh.read().splitlines()
    msg = "K8s generated webserver_config.py content error"
    assert received is not None and received.split("\n") == expected, msg
