"""`dagster.alerter` unit test cases.
"""
import os
import pathlib

import dagster.templater  # type: ignore[import]

TEMPLATE_PATH = os.path.join(
    pathlib.Path(__file__).resolve().parents[2], "src", "dagster", "config", "templates"
)


def test_notify_email() -> None:
    """Test notify_email."""
    # Given a email template file
    email_template_file = os.path.join(TEMPLATE_PATH, "email_html.j2")

    # when I generate the content
    body = dagster.templater.build_from_template({}, email_template_file)

    # then the result should not be None
    msg = "HTML email template should not be None"
    assert body, msg
