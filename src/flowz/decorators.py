"""Common decorators.

"""

from typing import Callable

from airflow.models import Variable


def dry_run(func: Callable | None = None) -> Callable | None:
    """Function decorator that looks within the `kwargs`
    parameter for the `dry` key and skips the function
    definition if set to `True.

    """

    def wrapped(self, *args, **kwargs) -> Callable | None:  # type: ignore[no-untyped-def]
        default_var = {"dry": False}
        config = Variable.get(
            self.dag_id, default_var=default_var, deserialize_json=True
        )
        is_dry = config.get("dry", False)
        self.log.info("Execution of %s running in dry mode?: %s", self, is_dry)

        func_to_run = None
        if not is_dry and func is not None:
            func_to_run = func(self, *args, **kwargs)

        return func_to_run

    return wrapped
