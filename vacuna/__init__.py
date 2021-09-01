"""Small library to work with dependencies in Python"""

import inspect
from typing import Callable, Dict

from .__version__ import __version__
from .lazy import Lazy, lazy, make_lazy

FACTORY = 'factory'

SINGLETON = 'singleton'

RESOURCE = 'resource'


class Dependency:
    def __init__(self, name: str):
        self.name = name
        self.kind = FACTORY

        self.fn = None
        self.args = None
        self.kwargs = None

    def validate(self):
        pass

    def set_fn(self, fn):
        self.fn = lazy(fn)

    def set_args(self, *args: Lazy, **kwargs: Lazy):
        self.args = args
        self.kwargs = kwargs

    def set_kind(self, kind: str):
        self.kind = kind

    def to_lazy(self):
        return self.fn(*self.args, **self.kwargs)

    def __call__(self):
        return self.to_lazy()()


class DependencyBuilder:
    def __init__(self, container: 'Container', kind=FACTORY, name=None):
        self.container = container
        self.kind = kind
        self.name = name

    def __call__(self, fn: Callable) -> Lazy:
        dependency = self.build_dependency(fn)

        return make_lazy(dependency, name=dependency.name)

    def build_dependency(self, fn) -> Dependency:
        name = self.get_name(fn)

        dependency = self.container.get_dependency(name)
        args, kwargs = self.get_dependencies(fn)

        dependency.set_kind(self.kind)
        dependency.set_fn(fn)
        dependency.set_args(*args, **kwargs)

        for arg in args:
            if isinstance(arg, Dependency):
                self.container.update_dependency(arg)

        for arg in kwargs.values():
            if isinstance(arg, Dependency):
                self.container.update_dependency(arg)

        self.container.update_dependency(dependency)

        return dependency

    def get_name(self, fn):
        if self.name is not None:
            return self.name
        return fn.__name__

    def get_dependencies(self, fn):
        args, _, _, defaults, *_ = inspect.getfullargspec(fn)

        if defaults is None:
            defaults = ()

        defaults = (None,) * (len(args) - len(defaults)) + defaults

        dependencies = []

        for arg, default in zip(args, defaults):
            if default is not None:
                dependencies.append(default)
            else:
                dependency = self.container.get_dependency(arg)
                dependencies.append(dependency)

        return dependencies, {}


class Container:
    def __init__(self):
        self._dependencies = {}  # type: Dict[str, Dependency]

    def dependency(self, kind=FACTORY, name=None) -> DependencyBuilder:
        return DependencyBuilder(self, kind=kind, name=name)

    def run(self, dependency: Dependency):
        dependency()

    def get_dependency(self, name: str) -> Dependency:
        return self._dependencies.get(name, Dependency(name))

    def update_dependency(self, dependency: Dependency):
        self._dependencies[dependency.name] = dependency


__all__ = ['__version__', 'Container']
