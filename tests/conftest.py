"""Global fixture arrangement.

"""
import os
import datetime
import tempfile
import shutil
import uuid
import logging
import pathlib
import pytest

import dagster.user
from dagster.utils import lazy
from dagster.utils.dagprimer import DagPrimer

DATA_INTERVAL_START = datetime.datetime(2021, 9, 13)
DATA_INTERVAL_END = DATA_INTERVAL_START + datetime.timedelta(days=1)

LAZY_ETLER_API = lazy.Loader('dagster.api', globals(), 'dagster.api')
LAZY_ETLER_VAR = lazy.Loader('dagster.variable', globals(), 'dagster.variable')


@pytest.fixture
def working_dir(request):
    """Temporary working directory.
    """
    def fin():
        """Tear down.
        """
        logging.info('Deleting temporary test directory: "%s"', dirpath)
        shutil.rmtree(dirpath)

    request.addfinalizer(fin)
    dirpath = tempfile.mkdtemp()
    logging.info('Created temporary test directory: "%s"', dirpath)

    return dirpath

LAZY_AF = lazy.Loader('airflow', globals(), 'airflow')
LAZY_TI = lazy.Loader('airflow.models.taskinstance', globals(), 'airflow.models.taskinstance')
LAZY_PYTHON_OPERATOR = lazy.Loader('airflow.operators.python',
                                       globals(),
                                       'airflow.operators.python')
LAZY_AF_UTILS = lazy.Loader('airflow.utils', globals(), 'airflow.utils')

CONFIG = os.path.join(pathlib.Path(__file__).resolve().parents[1], 'config')


@pytest.fixture
def bootstrap_authentication(request):
    """Load Airflow JSON auth definition into airflow.models.Variable DB.
    """
    def fin():
        """Tear down.
        """
        for user in dagster.user.list_airflow_users():
            dagster.user.delete_airflow_user(user)

    request.addfinalizer(fin)

    dag_name = 'bootstrap_load_authentication_fixture'
    description = """Bootstrap load-authentication fixture"""
    _dp = DagPrimer(dag_name=dag_name, department='FIXTURE', description=description)
    dag = LAZY_AF.DAG(_dp.dag_id, default_args=_dp.default_args, **(_dp.dag_properties))

    task = LAZY_PYTHON_OPERATOR.PythonOperator(
        task_id='task-authentication',
        python_callable=dagster.user.set_authentication,
        dag=dag)

    execution_date = _dp.default_dag_properties.get('start_date')
    _ti = LAZY_TI.TaskInstance(task=task, execution_date=execution_date)
    _ti.log.propagate = True
    _ti.run(ignore_ti_state=True)

    return _ti


@pytest.fixture
def bootstrap_connections(config_path):
    """Load Airflow JSON connection definitions into airflow.models.Connection DB.
    """
    dag_name = 'bootstrap_load_connection_fixture'
    description = """Bootstrap load-connection fixture"""
    _dp = DagPrimer(dag_name=dag_name, department='FIXTURE', description=description)
    dag = LAZY_AF.DAG(_dp.dag_id,default_args=_dp.default_args, **(_dp.dag_properties))

    task_id = 'load-connections'
    task = LAZY_PYTHON_OPERATOR.PythonOperator(
        task_id=task_id,
        python_callable=LAZY_ETLER_API.set_connection,
        op_args=[config_path or os.path.join(CONFIG, 'connections')],
        dag=dag)

    execution_date = _dp.default_dag_properties.get('start_date')
    execution_date_end = execution_date + datetime.timedelta(days=1)
    dagrun = dag.create_dagrun(state=LAZY_AF_UTILS.state.DagRunState.RUNNING,
                               execution_date=execution_date,
                               data_interval=(execution_date, execution_date_end),
                               start_date=execution_date_end,
                               run_type=LAZY_AF_UTILS.types.DagRunType.MANUAL)

    _ti = dagrun.get_task_instance(task_id=task_id)
    _ti.task = task
    _ti.log.propagate = True
    _ti.run(ignore_ti_state=True)

    return _ti


@pytest.fixture(scope='function')
def bootstrap_task_variables(request, config_path):
    """Load Airflow JSON task definitions into airflow.models.Variable DB.
    """
    def fin():
        """Tear down.
        """
        LAZY_ETLER_VAR.del_variable(config_path or os.path.join(CONFIG, 'tasks'))

    request.addfinalizer(fin)

    dag_name = f'bootstrap_load_task_variables_fixture-{str(uuid.uuid1())}'
    description = """Bootstrap load-task-variables fixture"""
    _dp = DagPrimer(dag_name=dag_name, department='FIXTURE', description=description)
    dag = LAZY_AF.DAG(_dp.dag_id, default_args=_dp.default_args, **(_dp.dag_properties))

    task_id = 'load-task-variables'
    task = LAZY_PYTHON_OPERATOR.PythonOperator(
        task_id=task_id,
        python_callable=LAZY_ETLER_VAR.set_variable,
        op_args=[config_path or os.path.join(CONFIG, 'tasks')],
        dag=dag)

    execution_date = _dp.default_dag_properties.get('start_date')
    execution_date_end = execution_date + datetime.timedelta(days=1)
    dagrun = dag.create_dagrun(state=LAZY_AF_UTILS.state.DagRunState.RUNNING,
                               execution_date=execution_date,
                               data_interval=(execution_date, execution_date_end),
                               start_date=execution_date_end,
                               run_type=LAZY_AF_UTILS.types.DagRunType.MANUAL)

    _ti = dagrun.get_task_instance(task_id=task_id)
    _ti.task = task
    _ti.log.propagate = True
    _ti.run(ignore_ti_state=True)

    return _ti


@pytest.fixture
def bootstrap_dag_variables(request, config_path):
    """Load Airflow JSON DAG definitions into airflow.models.Variable DB.
    """
    def fin():
        """Tear down.
        """
        LAZY_ETLER_VAR.del_variable(config_path or os.path.join(CONFIG, 'dags'))

    request.addfinalizer(fin)

    dag_name = 'bootstrap_load_dag_variables_fixture'
    description = """Bootstrap load-dag-variables fixture"""
    _dp = DagPrimer(dag_name=dag_name, department='FIXTURE', description=description)
    dag = LAZY_AF.DAG(_dp.dag_id,default_args=_dp.default_args, **(_dp.dag_properties))

    task_id = 'load-dag-variables'
    task = LAZY_PYTHON_OPERATOR.PythonOperator(
        task_id=task_id,
        python_callable=LAZY_ETLER_VAR.set_variable,
        op_args=[config_path or os.path.join(CONFIG, 'dags')],
        dag=dag)

    execution_date = _dp.default_dag_properties.get('start_date')
    execution_date_end = execution_date + datetime.timedelta(days=1)
    dagrun = dag.create_dagrun(state=LAZY_AF_UTILS.state.DagRunState.RUNNING,
                               execution_date=execution_date,
                               data_interval=(execution_date, execution_date_end),
                               start_date=execution_date_end,
                               run_type=LAZY_AF_UTILS.types.DagRunType.MANUAL)

    _ti = dagrun.get_task_instance(task_id=task_id)
    _ti.task = task
    _ti.log.propagate = True
    _ti.run(ignore_ti_state=True)

    return _ti


@pytest.fixture()
def task_variables(request, config_path) -> int:
    """Airflow Variables load and delete.

    """
    def fin():
        """Clear out loaded Airflow variables from DB.
        """
        LAZY_ETLER_VAR.del_variable(config_path)

    request.addfinalizer(fin)
    counter = LAZY_ETLER_VAR.set_variable(config_path)

    return counter


@pytest.fixture(scope='session')
def dagbag():
    """Set up the Airflow DagBag common to pytest.Session.

    """
    af_models = lazy.Loader('models', globals(), 'airflow.models')

    return af_models.DagBag()


def pytest_sessionstart(session) -> None: # pylint: disable=unused-argument
    """Set up the Airflow context with appropriate config for test.

    """
    airflow_home = tempfile.mkdtemp()
    os.environ['AIRFLOW_HOME'] = airflow_home
    logging.info('Temporary Airflow home (AIRFLOW_HOME): "%s"', airflow_home)

    project_dir = os.environ.get('PROJECT_SOURCE_DIR')
    if not project_dir:
        cwd = pathlib.Path.cwd()
        project_dir = os.path.join(cwd, cwd.resolve().name.lower().replace('-', '_'))
    logging.info('Airflow project directory: "%s"', project_dir)

    os.environ['AIRFLOW__CORE__UNIT_TEST_MODE'] = 'true'
    os.environ['AIRFLOW__CORE__DAGS_FOLDER'] = os.path.join(project_dir, 'dags')
    os.environ['AIRFLOW__CORE__PLUGINS_FOLDER'] = os.path.join(project_dir, 'plugins')
    os.environ['AIRFLOW__CORE__LOAD_EXAMPLES'] = 'false'
    os.environ['AIRFLOW__CORE__FERNET_KEY'] = 'LFKF4PSrAOG-kbxOouoLj8Du2QCnsp9qw7G21-WPsLU='
    os.environ['AIRFLOW__DATABASE__LOAD_DEFAULT_CONNECTIONS'] = 'false'
    db_url = f'sqlite:///{airflow_home}/airflow.db'
    os.environ['AIRFLOW__DATABASE__SQL_ALCHEMY_CONN'] = db_url

    os.environ['AIRFLOW_HOME'] = airflow_home
    if os.environ.get('AIRFLOW_PRIME_TEST_CONTEXT') == 'true':
        utils_db = lazy.Loader('utils_db', globals(), 'airflow.utils.db')
        utils_db.upgradedb()


def pytest_sessionfinish(session, exitstatus) -> None: # pylint: disable=unused-argument
    """Tear down the Airflow context.

    """
    logging.info('Deleting working temporary test directory: "%s"', os.environ['AIRFLOW_HOME'])
    shutil.rmtree(os.environ['AIRFLOW_HOME'])
