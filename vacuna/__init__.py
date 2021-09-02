"""Small library to work with dependencies in Python"""

import inspect
from typing import Callable, Dict, Optional, Tuple

from typing_extensions import Literal

from .__version__ import __version__
from .lazy import Lazy, lazy, make_lazy, once

Kind = Literal['factory', 'singleton', 'resource']

FACTORY = 'factory'  # type: Kind
SINGLETON = 'singleton'  # type: Kind
RESOURCE = 'resource'  # type: Kind


class Dependency:
    def __init__(self, name: str):
        self.name = name
        self.kind = FACTORY

        self.fn = None  # type: Optional[Callable]
        self.args = None  # type: Optional[Tuple[Lazy, ...]]
        self.kwargs = None  # type: Optional[Dict[str, Lazy]]

    def validate(self):
        pass

    def set_values(self, fn: Callable, kind: Kind, *args: Lazy, **kwargs: Lazy):
        self.fn = lazy(fn)  # TODO: do not use lazy here
        self.args = args
        self.kwargs = kwargs
        self.kind = kind

        self.lazy_fn = lambda: \
            self.fn(*self.args, **self.kwargs)  # type: ignore

        if self.kind == 'SINGLETON':
            self.lazy_fn = once(self.lazy_fn)

    def __call__(self):
        return self.lazy_fn()()


class DependencyBuilder:
    def __init__(self, container: 'Container', kind: Kind = FACTORY, name=None):
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

        dependency.set_values(fn, self.kind, *args, **kwargs)

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
        signature = inspect.signature(fn)

        dependencies = []

        for parameter in signature.parameters.values():
            name = parameter.name
            default = parameter.default

            if default is not inspect._empty:
                dependencies.append(default)
            else:
                dependency = self.container.get_dependency(name)
                dependencies.append(dependency)

        return dependencies, {}


class Container:
    def __init__(self):
        self._dependencies = {}  # type: Dict[str, Dependency]

    def dependency(self, kind: Kind = FACTORY, name=None) -> DependencyBuilder:
        return DependencyBuilder(self, kind=kind, name=name)

    def run(self, dependency: Dependency):
        dependency()

    def get_dependency(self, name: str) -> Dependency:
        return self._dependencies.get(name, Dependency(name))

    def update_dependency(self, dependency: Dependency):
        self._dependencies[dependency.name] = dependency


__all__ = ['__version__', 'Container']
