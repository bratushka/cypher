import abc
import collections
import json
import itertools
import math
import string
from typing import Any, Iterable, Generator, Mapping, Tuple, Union

from neo4j.v1 import GraphDatabase


class DatabaseAddressException(Exception):
    pass


def generate_tags(number: int) -> Generator[str, None, None]:
    length = math.ceil(math.log(number, 26)) if number > 1 else 1

    return (
        ''.join(x)
        for x in itertools.product(string.ascii_lowercase, repeat=length)
    )


class BaseProp(abc.ABC):
    valid_types = ()

    def __init__(self, *, required: bool=False):
        self.required = required

    @classmethod
    def validate(cls, key: str, value: Any, model_name: str):
        if not any(isinstance(value, t) for t in cls.valid_types):
            error_text = (
                'Trying to assign a value of type `{}` to the `{}`'
                ' property of `{}`. Valid types are: {}.'
            ).format(
                type(value).__name__,
                key,
                model_name,
                ', '.join(map(lambda t: t.__name__, cls.valid_types))
            )
            raise TypeError(error_text)


class Props:
    """
    Unique class for properties for nodes and edges.
    """
    class Boolean(BaseProp):
        valid_types = (bool,)

    class Integer(BaseProp):
        valid_types = (int,)

    class Float(BaseProp):
        valid_types = (int, float)

    class String(BaseProp):
        valid_types = (str,)


class Model:
    """
    Common logic for Node and Edge.
    """
    def __init__(self, *, labels: Iterable[str]=None, **kwargs):
        self.id = None
        self._labels = None
        self.labels = labels
        self._extra_props = {}

        for key, value in kwargs.items():
            prop = getattr(self.__class__, key, None)
            if isinstance(prop, BaseProp):
                prop.validate(key, value, self.__class__.__name__)
                setattr(self, key, value)
            else:
                self._extra_props[key] = value

    @property
    def labels(self) -> Tuple[str, ...]:
        return self._labels

    @labels.setter
    def labels(self, value: Iterable[str]):
        if value is None:
            value = ()
        if not all(isinstance(v, str) for v in value):
            raise TypeError('labels should be an iterable if strings')

        extra_labels = tuple(
            identifier
            for identifier in value
            if identifier != self.__class__.__name__
        )

        self._labels = (self.__class__.__name__,) + extra_labels

    # @TODO: remove this, use Query.represent() instead
    def cypherify(self) -> str:
        def normalize(value: str) -> str:
            return value.replace('`', '``')

        labels = ''.join(
            ':`{}`'.format(normalize(label))
            for label in self.labels
        )

        prop_keys = sorted(
            key for
            key in dir(self)
            if isinstance(getattr(self.__class__, key, None), BaseProp)
        )
        import json
        props = ', '.join(
            ': '.join(('`' + key + '`', json.dumps(getattr(self, key))))
            for key in prop_keys
        )

        return ' '.join((labels, '{', props, '}'))

    def __hash__(self):
        return id(self)

    def __str__(self):
        return self.cypherify()


class Node(Model):
    """
    Python representation of a node in graph.
    """
    # @TODO: remove this, use Query.represent() instead
    def wrap(self, tag: str= '') -> str:
        return '({}{})'.format(tag, self.cypherify())


class Edge(Model):
    """
    Python representation of an edge in graph.
    """
    def __init__(self, from_node: Model, to_node: Model, **kwargs):
        self.nodes = (from_node, to_node)
        super().__init__(**kwargs)

    # @TODO: remove this, use Query.represent() instead
    def wrap(self, tag: str= '', frm: str= '', to: str= '') -> str:
        return ''.join((
            '({})-'.format(frm),
            '[{}{}]'.format(tag, self.cypherify()),
            '->({})'.format(to),
        ))


class Query:
    """
    Utilities to generate
    """
    @staticmethod
    def represent(
        obj: Union[Node, Edge],
        var: str='',
        from_var: str='',
        to_var: str='',
    ) -> str:
        def normalize(value: str) -> str:
            return value.replace('`', '``')

        if not isinstance(obj, (Node, Edge)):
            raise TypeError

        labels = ''.join(
            ':`{}`'.format(normalize(label))
            for label in obj.labels
        )

        prop_keys = sorted(
            key for
            key in dir(obj)
            if isinstance(getattr(obj.__class__, key, None), BaseProp)
        )
        props = ', '.join(
            ': '.join(('`' + key + '`', json.dumps(getattr(obj, key))))
            for key in prop_keys
        )
        body = ' '.join((labels, '{', props, '}'))

        if isinstance(obj, Node):
            return '({}{})'.format(var, body)
        return ''.join((
            '({})-'.format(from_var),
            '[{}{}]'.format(var, body),
            '->({})'.format(to_var),
        ))


class DB:
    """
    The class to be used for building queries.

    Example of usage:
    data = (DB()
        .match(User, 'a')
        .where(User.dob > 123123)
        .connected(Parent, 'b')
        .where(Parent.q == 2)
        .to(User, 'c')
        .where(User.dob < 4)
        .where('a.dob == b.dob')
        .result()
    )
    """
    url = None
    host = 'cypher-db'
    port = 7687
    user = 'neo4j'
    password = 'cypher'

    def __init__(self):
        self._driver = GraphDatabase.driver(
            self._get_url(),
            auth=(self.user, self.password)
        )

        self._action: str = None
        self._models: Tuple[Model, ...] = None

    @classmethod
    def _get_url(cls) -> str:
        if cls.url:
            if not cls.url.startswith('bolt://'):
                raise DatabaseAddressException('Please, use bolt protocol')
            return cls.url

        return ''.join((
            '' if cls.host.startswith('bolt://') else 'bolt://',
            cls.host,
            ':',
            str(cls.port),
        ))

    @property
    def models(self) -> Tuple[Model, ...]:
        return self._models

    @models.setter
    def models(self, value: Iterable[Model]):
        if not all(isinstance(model, (Node, Edge)) for model in value):
            error_str = 'Only `Node` and `Edge` instances can be used in query'
            raise TypeError(error_str)

        self._models = tuple(sorted(value, key=lambda x: isinstance(x, Edge)))

    @staticmethod
    def _get_model_tags(
        node_map: Mapping[Model, str],
        model: Model,
    ) -> Tuple[str, ...]:
        if isinstance(model, Edge):
            return (
                node_map[model],
                node_map[model.nodes[0]],
                node_map[model.nodes[1]],
            )
        return node_map[model],

    @property
    def query(self) -> str:
        tags = generate_tags(len(self.models))
        node_map = collections.OrderedDict()

        # First: add all the nodes.
        for model in self.models:
            if isinstance(model, Edge):
                node_map.update((m, None) for m in model.nodes)
            else:
                node_map[model] = None
        # Second: add all the labels.
        for model in self.models:
            if isinstance(model, Edge):
                node_map[model] = None
        # Third: add a tag to each of the models.
        for key in node_map.keys():
            node_map[key] = next(tags)

        return ''.join((
            self._action,
            ', '.join(
                k.wrap(*self._get_model_tags(node_map, k))
                for k, v in node_map.items()
            ),
            '\nRETURN ',
            ', '.join(node_map.values()),
        ))

    def match(self, *models: Model):
        self._action = 'MATCH '
        self.models = models

        return self

    def create(self, *models: Model) -> 'DB':
        self._action = 'CREATE '
        self.models = models

        return self
