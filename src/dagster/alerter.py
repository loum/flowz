"""Custom Airflow alerting.

"""

from pathlib import Path, PurePath
import os

from airflow.utils.email import send_email
import airflow.utils.context

import dagster.templater


def notify_email(context: airflow.utils.context.Context) -> None:
    """Send custom email alerts."""
    _ti = context.get("ti")

    if _ti is not None:
        title = f"Airflow Alert: {_ti.dag_id}:{_ti.task_id} Failure"

        ti_map = {
            "dag_id": _ti.dag_id,
            "task_id": _ti.task_id,
            "execution_date": _ti.execution_date,
            "start_date": _ti.start_date,
            "end_date": _ti.end_date,
            "duration": _ti.duration,
            "log_url": _ti.log_url,
        }
        email_template_file = PurePath(Path(__file__).resolve().parents[0]).joinpath(
            "config",
            "templates",
            "email_html.j2",
        )
        body = dagster.templater.build_from_template(ti_map, str(email_template_file))

        send_email(os.environ.get("AIRFLOW_SUPPORT_EMAIL", ""), title, body)
