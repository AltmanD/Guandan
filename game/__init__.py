__author__ = 'Lu Yudong'

from collections import defaultdict
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union


def klass(typename: str, field_names: List[str], *, init=None) -> type:
    """Dynamic class.
    Args:
        typename (str): The name of the class.
        field_names (List[str]): The names of the fields.
        init (Optional[Callable]): The init function.
    Returns:
        type: The class.
    """
    repr_fmt = '(' + ', '.join(f'{name}=%r' for name in field_names) + ')'

    def constructor(self, *args, **kwargs):
        if init is not None:
            ret = init()
            if isinstance(ret, (list, tuple)):
                ret = {k: v for k, v in zip(field_names, ret)}
            if isinstance(ret, dict):
                ret.update(kwargs)
                kwargs = ret
            else:
                raise ValueError(f'Unexpected return value from init: {ret!r}')
        for i, name in enumerate(field_names):
            if i < len(args):
                setattr(self, name, args[i])
            elif name in kwargs:
                setattr(self, name, kwargs[name])
            else:
                raise ValueError(f'No value for field {name!r}')

    def __repr__(self):
        return self.__class__.__name__ + repr_fmt % tuple(getattr(self, name) for name in field_names)

    klass_namespace = {
        '__init__': constructor,
        '__repr__': __repr__,
    }

    return type(typename, (object,), klass_namespace)


Context = klass('Context', [
    'n_entities',
    'entity_types',
    'component_types',
    'entity_names',
    'entity_by_name',
    'entity_components',
    'entity_components_by_type',
    'systems',
], init=lambda: [
    0,
    {},
    {},
    {},
    {},
    {},
    {},
    {},
])