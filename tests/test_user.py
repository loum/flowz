"""Unit test cases for `dagster.user`.
"""

import dagster.user  # type: ignore[import]


def test_user() -> None:
    """Add user via RBAC user."""
    # When I insert a user into the RBAC DB
    received = dagster.user.set_admin_user("airflow", "airflow")

    # the system should not return an error
    msg = "Adding Airflow user should not return False"
    assert received, msg

    # when I query the user post-insert DB
    # I should receive a user name
    received = dagster.user.list_airflow_users()
    msg = 'Expecting "airflow" user'
    assert received == ["airflow"], msg

    # when I delete the user
    dagster.user.delete_airflow_user("airflow")

    # there response should be an empty list
    received = dagster.user.list_airflow_users()
    msg = "Expecting no user"
    assert [x.username for x in received] == [], msg
