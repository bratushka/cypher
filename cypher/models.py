"""
Objects representing the cypher nodes and edges.
"""
from typing import Any, Iterable, Mapping, MutableMapping, MutableSet

from .props import BaseProp


class Model:
    """
    Common logic for Node and Edge.
    """
    class Meta:
        """
        Meta data for the model.
        """
        unique_together = ()
        validations = ()
        abstract = True
        database = 'default'

    def __init__(self, **kwargs):
        self._labels: MutableSet[str] = {self.__class__.__name__}
        self._props: MutableMapping[str, Any] = {}

        cls = type(self)
        model_props = {
            prop: getattr(self, prop)
            for prop in dir(cls)
            if isinstance(getattr(self, prop), BaseProp)
        }

        for name, prop in model_props.items():
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

        self.props = {
            prop: value
            for prop, value in kwargs.items()
            if prop not in model_props
        }

    @property
    def labels(self) -> MutableSet[str]:
        """
        :return: labels of the model
        """
        return self._labels

    @labels.setter
    def labels(self, value: Iterable[str]):
        """
        Set the labels to the model.
        """
        if not all(isinstance(name, str) for name in value):
            raise TypeError('Labels can only be of type `str`')

        self._labels = {self.__class__.__name__, *value}

    @property
    def props(self) -> MutableMapping[str, Any]:
        """
        :return: arbitrary props of the model.
        """
        return self._props

    @props.setter
    def props(self, value: Mapping[str, Any]):
        """
        Set arbitrary props of the model.
        """
        # @TODO: check the value for acceptable types (both keys and values).
        # @TODO: all of the prop names should not match any model's prop.
        self._props = value


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
