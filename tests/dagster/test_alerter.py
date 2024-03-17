"""`dagster.alerter` unit test cases.
"""

from pathlib import Path, PurePath

import dagster.templater  # type: ignore[import]

TEMPLATE_PATH = PurePath(Path(__file__).resolve().parents[2]).joinpath(
    "src", "dagster", "config", "templates"
)


def test_notify_email() -> None:
    """Test notify_email."""
    # Given a email template file
    email_template_file = str(TEMPLATE_PATH.joinpath("email_html.j2"))

    # when I generate the content
    body = dagster.templater.build_from_template({}, email_template_file)

    # then the result should not be None
    assert body, "HTML email template should not be None"
