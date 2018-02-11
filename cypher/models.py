"""
Objects representing the cypher nodes and edges.
"""
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    MutableMapping,
    MutableSet,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

from .props import BaseProp


class Model:
    """
    Common logic for Node and Edge.
    """
    class Meta:
        """
        Meta data for the model.
        """
        primary_key: str = None
        unique_together: Iterable[str] = ()
        validations: Iterable[Callable] = ()
        abstract: bool = True
        database: str = 'default'

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
                normalized = prop.value_type.normalize(value)
                prop.value_type.validate(normalized)
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


class ModelDetails:
    """
    Organized details of a pattern unit.
    """
    __slots__ = ['var', 'type', 'instance', 'conn']

    def __init__(
            self,
            identifier: Union[Edge, Node, Type[Edge], Type[Node]],
            var: str,
            conn: Tuple[Optional[int], Optional[int]] = None,
    ):
        self.var = var

        if isinstance(identifier, (Node, Edge)):
            self.type = type(identifier)
            self.instance = identifier
        elif issubclass(identifier, (Node, Edge)):
            self.type = identifier
            self.instance = None
        else:
            raise TypeError
        # self.start: Optional[str] = None
        # self.end: Optional[str] = None
        self.conn = conn

    def get_labels(self) -> List[str]:
        """
        :return: sorted tuple of labels
        """
        if self.instance:
            return sorted(self.instance.labels)
        elif self.type is Edge or self.type is Node:
            return []
        return [self.type.__name__]

    def get_var_and_labels(self) -> str:
        """
        Get a string ready to be used in cypher pattern.
        Example: `a:Human:Person`.
        """
        return ':'.join((self.var, *self.get_labels()))
