"""Delay imports of Python modules and packages.

"""
import types
import importlib


class Loader(types.ModuleType):
    """Lazily import a module.

    """
    def __init__(self, local_name, parent_module_globals, module_name):
        self.__local_name = local_name
        self.__parent_module_globals = parent_module_globals

        super().__init__(module_name)

    @property
    def local_name(self):
        """:attr:`__local_name`
        """
        return self.__local_name

    @property
    def parent_module_globals(self):
        """:attr:`__parent_module_globals`
        """
        return self.__parent_module_globals

    def _load(self):
        """Import the target module and insert it into the parent's namespace.

        method will update this object's dict so that if someone keeps a reference to the
        LazyLoader, lookups are efficient (__getattr__ is only called on lookups that fail).
        """
        module = importlib.import_module(self.__name__)
        self.parent_module_globals[self.local_name] = module

        self.__dict__.update(module.__dict__)

        return module

    def __getattr__(self, item):
        module = self._load()

        return getattr(module, item)
