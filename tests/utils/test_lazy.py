"""Unit test cases for :class:`dagster.utils.lazy`.
"""
from dagster.utils import lazy


def test_lazy_init():
    """Initialise a elter.utils.lazy.Loader object.
    """
    # Given a Python module
    local_name = 'ospath'

    # and a Python module to lazy import
    module_name = 'os.path'

    # when I initialise a dagster.utils.Loader
    _ospath = lazy.Loader(local_name, globals(), module_name)

    # I should get an airflow.models instance
    msg = 'Object is not an dagster.utils.lazy.Loader instance'
    assert isinstance(_ospath, lazy.Loader), msg

    # and after invocation I can use an os.path function
    msg = 'os.path.exists() did not return expected value'
    assert _ospath.exists(__file__), msg
