# Integrating DAGs into the test harness

Recall that the new `sample` DAG is just Python logic. As such, it can be validated by running the test harness:

``` sh
make tests
```

Note that with the addition of the new `sample` DAG, Flowz has detected the change to the [Airflow DagBag](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/dagbag/index.html){target="blank"}. The test harness will fail as a results:

``` python title="New DAG fails the test harness."
E       AssertionError: DagBag to "DAG_TASK_IDS" control list mis-match: check the DAG names defined by DAG_TASK_IDS in fixtures. Or, add to "dag_names_to_skip" in the test_dagbag_set() test to skip the check.
E       assert ['ADMIN_BOOTSTRAP_LOCAL', 'ADMIN_SAMPLE_LOCAL']i == ['ADMIN_BOOTSTRAP_LOCAL']
E
E         Left contains one more item: 'ADMIN_SAMPLE_LOCAL'
E
E         Full diff:
E           [
E               'ADMIN_BOOTSTRAP_LOCAL',
E         +     'ADMIN_SAMPLE_LOCAL',
E           ]

tests/flowz/dags/test_dags.py:35: AssertionError

 tests/flowz/dags/test_dags.py::test_dagbag_set ⨯
```

If the new DAG will form part of production deployments, then you may consider adding the appropriate coverage in the test. This way, the test harness will safeguard against syntastic errors and incorrect deletions. To do so, you will need to add an entry to the `DAG_TASK_IDS`:

``` python title="DAG_TASK_IDS in tests/flowz/dags/conftest.py"
--8<-- "tests/flowz/dags/conftest.py:dag_task_ids"
```

Note that `DAG_TASK_IDS` is a dictionary based data structure that takes the DAG name as the key and the task names as values. Add the following to the `DAG_TASK_IDS`:

``` python title="Adding new DAG to DAG_TASK_IDS"
DAG_TASK_IDS = {
--8<-- "tests/flowz/dags/conftest.py:admin_bootstrap_local"
    "ADMIN_SAMPLE_LOCAL": [
        "end"
        "start",
    ],
}
```

Subsequent test harness passes should now complete successfully.

Alternatively, you can skip the validation of the DAG in the test harness by adding the name of the DAG to the `dag_names_to_skip`variable in the test. This is an empty list by default as follows:

``` python title="Skip DAG definition in the DagBag set validation."
--8<-- "tests/flowz/dags/test_dags.py:test_dagbag_set"
```

The following adjustment will suppress the DAG check:
``` python
    ...
    # less the DAG names that can be skipped from the check
    dag_names_to_skip: list[str] = ["ADMIN_SAMPLE_LOCAL"]
    ...
```
