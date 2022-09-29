"""Custom Airflow alerting.

"""
import os
import pathlib
from airflow.utils.email import send_email

import dagster.utils.templater

def notify_email(context):
    """Send custom email alerts.

    """
    _ti = context.get('ti')

    title = f'Airflow Alert: {_ti.dag_id}:{_ti.task_id} Failure'

    ti_map = {
        'dag_id': _ti.dag_id,
        'task_id': _ti.task_id,
        'execution_date': _ti.execution_date,
        'start_date': _ti.start_date,
        'end_date': _ti.end_date,
        'duration': _ti.duration,
        'log_url': _ti.log_url,
    }
    email_template_file = os.path.join(pathlib.Path(__file__).resolve().parents[0],
                                       'config',
                                       'templates',
                                       'email_html.j2')
    body = dagster.utils.templater.build_from_template(ti_map, email_template_file)

    send_email(os.environ.get('AIRFLOW_SUPPORT_EMAIL', ''), title, body)
