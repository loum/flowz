"""Unit test cases for `dagster.user`.
"""

import dagster.user


def test_user() -> None:
    """Add user via RBAC user."""
    # When I insert a user into the RBAC DB
    airflow_user: str = dagster.user.set_admin_user("airflow", "airflow")

    # the system should not return an error
    msg = "Adding Airflow user should not return False"
    assert airflow_user, msg

    # when I query the user post-insert DB
    # I should receive a user name
    all_users: list[str] = dagster.user.list_airflow_users()
    msg = 'Expecting "airflow" user'
    assert all_users == ["airflow"], msg

    # when I delete the user
    dagster.user.delete_airflow_user("airflow")

    # there response should be an empty list
    all_users = dagster.user.list_airflow_users()
    msg = "Expecting no user"
    assert all_users == [], msg
