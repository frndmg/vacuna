"""A lazy object is a deferred computation, `lambda: 2+2` is a deferred
computation for example, nothing will be called until we execute"""


from abc import ABC, abstractmethod
from functools import wraps
from operator import add, and_, attrgetter, itemgetter, mul, or_, sub


class Lazy(ABC):
    """Lazy object representation

    Convert a deferred computation into a lazy object using `make_lazy`.

    Examples:

    ```python
    >>> isinstance(make_lazy(lambda: 1), Lazy)
    True
    >>> isinstance(lambda: 1, Lazy)
    True

    ```

    ```python
    >>> x = make_lazy(lambda: 1)
    >>> y = lambda: 2
    >>> z = x + y
    >>> z()
    3

    ```
    """

    def __getattr__(self, attr) -> 'Lazy':
        return _make_lazy(
            once(_map_lazy(attrgetter(attr), self)),
            name=f'{self}.{attr}',
        )

    def __getitem__(self, item) -> 'Lazy':
        return _make_lazy(
            once(_map_lazy(itemgetter(item), self)),
            name=f'{self}[{repr(item)}]',
        )

    def __add__(self, other):
        return _make_lazy(
            once(_lazy_add(self, other)),
            name=f'({self} + {other})',
        )

    def __repr__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __call__(self):
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Lazy:
            if any('__call__' in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented


class LazyError(Exception):
    pass


def lazy(f):
    """Creates a lazy callable from a function

    Examples:


    ```python
    >>> from collections import namedtuple
    >>> X = lazy(namedtuple('X', 'a b'))
    >>> a = lambda: 1
    >>> b = lambda: 'foo'

    ```

    The reference is the same after constructing the object

    ```python
    >>> c = X(a, b=b)
    >>> c() is c()
    True

    ```

    ```python
    >>> c1 = X(a, b=b)
    >>> c2 = X(a, b=b)
    >>> c1() is c2()
    False

    ```

    You can also use non lazy objects

    ```python
    >>> c = X(a, b=2)
    >>> c()
    X(a=1, b=2)

    ```

    Be careful with mutations

    ```python
    >>> c = X(a=make_lazy(lambda: [1]), b=2)
    >>> d = c()
    >>> d.a[0] = 3
    >>> c()
    X(a=[3], b=2)

    ```
    """
    @wraps(f)
    def _lazy(*args, **kwargs):
        return make_lazy(
            lambda: f(
                *map_list(args, call_if_lazy),
                **map_dict(kwargs, call_if_lazy)
            ),
            name=f.__name__,
        )

    return _lazy


def make_lazy(lazy_obj, name=''):
    """Creates a Lazy object that lets you inspect the properties of the object
    in a lazy fashion.

    Examples:

    ```python
    >>> x = make_lazy(lambda: {'a': [{'b': True}]})
    >>> y = x['a'][0]['b']
    >>> y()
    True

    ```

    ```python
    >>> from collections import namedtuple
    >>> X = namedtuple('X', 'a b')
    >>> x = make_lazy(lambda: X(a=[{'b': True}], b=False))
    >>> y = x.a[0]['b']
    >>> y()
    True

    ```

    ```python
    >>> y = x.a[1]['b']  # this line does not break
    >>> y()
    Traceback (most recent call last):
      ...
    vacuna.lazy.LazyError: error when evaluating `.a[1]`

    ```

    ```python
    >>> x = make_lazy(lambda: 2)
    >>> y = make_lazy(lambda: 1)
    >>> z = x + y
    >>> z()
    3

    ```

    ```python
    >>> x = make_lazy(lambda: [])
    >>> x()
    []
    >>> x() is x()
    True

    ```
    """
    return _make_lazy(once(lazy_obj), name)


def _make_lazy(lazy_obj, name=''):
    class _Lazy(Lazy):
        def __repr__(self):
            return name

        def __call__(self):
            try:
                return lazy_obj()
            except LazyError:
                raise
            except Exception as e:
                raise LazyError(f'error when evaluating `{name}`') from e

    return _Lazy()


def once(f):
    """Execute the given function only once and cache the result

    Examples:

    Without `once`

    ```python
    >>> def f(x=[]):
    ...     x.append(1)
    ...     return x
    >>> f()
    [1]
    >>> f()
    [1, 1]

    ```

    With `once`

    ```python
    >>> @once
    ... def f(x=[]):
    ...     x.append(1)
    ...     return x
    >>> f()
    [1]
    >>> f()
    [1]

    ```

    """

    x = None
    executed = False

    def _once():
        nonlocal x, executed

        if not executed:
            x = f()
            executed = True

        return x

    return _once


def map_list(xs, f):
    return tuple(f(x) for x in xs)


def map_dict(d, f):
    return dict((k, f(v)) for k, v in d.items())


def call_if_lazy(x):
    if isinstance(x, Lazy):
        return x()
    return x


def _map_lazy(f, lazy_x):
    return lambda: f(call_if_lazy(lazy_x))


def _lazy_add(x, y):
    return lambda: add(call_if_lazy(x), call_if_lazy(y))


def _lazy_sub(x, y):
    return lambda: sub(call_if_lazy(x), call_if_lazy(y))


def _lazy_mul(x, y):
    return lambda: mul(call_if_lazy(x), call_if_lazy(y))


def _lazy_and_(x, y):
    return lambda: and_(call_if_lazy(x), call_if_lazy(y))


def _lazy_or_(x, y):
    return lambda: or_(call_if_lazy(x), call_if_lazy(y))
