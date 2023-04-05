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
    'entity_index',
    'entity_name',
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


def entity_add(ctx: Context, name: Optional[str] = None) -> int:
    """Add an entity to the context.

    Args:
        ctx (Context): The context.
        name (Optional[str], optional): The name of the entity. Defaults to None.

    Returns:
        int: The entity ID.

    Raises:
        ValueError: If the entity name already exists.
    """
    if name is not None and name in ctx.entity_by_name:
        raise ValueError(f'Entity with name {name!r} already exists') from None
    eid = ctx.n_entities
    ctx.n_entities += 1
    ctx.entity_names[eid] = name
    if name is not None:
        ctx.entity_by_name[name] = eid
    ctx.entity_components[eid] = {}
    ctx.entity_components_by_type[eid] = defaultdict(list)
    return eid


def entity_get_all(ctx) -> Iterator[int]:
    """Get all entity IDs.

    Args:
        ctx (Context): The context.

    Returns:
        Iterator[int]: The entity IDs.
    """
    return ctx.entity_names.keys()


def entity_remove(ctx: Context, eid: int) -> None:
    """Remove an entity from the context.

    Args:
        ctx (Context): The context.
        eid (int): The entity ID.

    Raises:
        ValueError: If the entity does not exist.
    """
    try:
        name = ctx.entity_names.pop(eid)
    except KeyError:
        _exception_entity_not_exist(eid)
    if name is not None:
        del ctx.entity_by_name[name]
    del ctx.entity_components[eid]
    del ctx.entity_components_by_type[eid]


def _exception_entity_not_exist(eid: int):
    raise ValueError(f'Entity {eid} does not exist') from None