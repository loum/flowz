# Dagster conventions

Airflow as a workflow management system can be utilised as shared infrastructure between different teams and entities within the organisation. Having more contributors to the platform introduces a communal aspect where everyone can create and leverage existing code and tooling. However, as the number of DAGs begins to increase, so too could the maintenance burden. As such, it is recommended to adopt a set of development principles to ensure a degree of consistency within the framework. The following guidelines are a default recommendation.

## Things to consider when creating your DAGs

### Distinction between DAGs and tasks
A simple strategy that is utilised in Dagster is to capitalise DAG names and set task names to lower case.

### Naming standards
The DAG name (Python module name) plays an integral part in the operation of Airflow. It is also the token that presents in the Airflow web UI.

The DAG names are made up of three components separated by underscores (`_`):

1. Department or team name (`department` parameter to `dagster.Primer`)
1. Short name to give DAG some operational context (`dag_name` parameter to `dagster.Primer`)
1. Environment is added automatically based on the setting of the environment variable `AIRFLOW_CUSTOM_ENV` (defaults to `local`)

For example, the DAG name generated from the `src/dagster/dags/template.py` becomes `ADMIN_TEMPLATE_LOCAL`

!!! note
    Ensure the `dag_name` and `department` combination is unique amongst all DAGS under ``AIRFLOW__CORE__DAGS_FOLDER`` as this could cause an implicit conflict that is difficult to troubleshoot.
