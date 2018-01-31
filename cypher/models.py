"""
Objects representing the cypher nodes and edges.
"""
import uuid
from typing import Mapping

from .props import BaseProp, Props


class Model:
    """
    Common logic for Node and Edge.
    """
    uid = Props.String()

    class Meta:
        """
        Meta data for the model.
        """
        unique_together = ()
        validations = ()
        abstract = True
        database = 'default'

    def __init__(self, **kwargs):
        cls = type(self)
        props: Mapping[str, BaseProp] = {
            prop: getattr(self, prop)
            for prop in dir(cls)
            if isinstance(getattr(self, prop), BaseProp)
        }
        if 'uid' not in kwargs:
            kwargs['uid'] = uuid.uuid4().hex

        for name, prop in props.items():
            value = kwargs.get(name, prop.default)

            if value is not None:
                normalized = prop.normalize(value)
                prop.validate(normalized)
                setattr(self, name, normalized)
            elif value is None and not prop.required:
                setattr(self, name, None)
            else:
                error_text = (
                    'Cannot initialize a `{}` without `{}`'
                    .format(cls.__name__, name)
                )
                raise ValueError(error_text)


class Node(Model):
    """
    Pythonic representation of a graph node.
    """
    pass


class Edge(Model):
    """
    Pythonic representation of a graph edge.
    """
    pass
