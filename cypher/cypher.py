import abc
import itertools
import math
import string
from typing import Any, Iterable, Generator, Tuple

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
    def labels(self) -> tuple:
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

    def cypher_repr(self) -> str:
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

    def __str__(self):
        return self.cypher_repr()


class Node(Model):
    """
    Python representation of a node in graph.
    """


class Edge(Model):
    """
    Python representation of an edge in graph.
    """


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

        self._action = None
        self._models: Tuple[Model] = ()

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
    def models(self) -> Tuple[Model]:
        return self._models

    @models.setter
    def models(self, value: Iterable[Model]):
        self._models = tuple(sorted(value, key=lambda x: isinstance(x, Edge)))

    @property
    def query(self) -> str:
        tags = generate_tags(len(self.models))

        models = []
        tag_list = []
        for model in self.models:
            tag = next(tags)
            tag_list.append(tag)
            models.append(
                ('({}{})' if isinstance(model, Node) else '[{}{}]')
                .format(tag, model.cypher_repr())
            )

        return ''.join((
            'CREATE ',
            ', '.join(models),
            '\nRETURN ',
            ', '.join(tag_list),
        ))

    def __repr__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def match(self):
        raise NotImplementedError

    def create(self, *models: Model) -> 'DB':
        self._action = 'CREATE'
        self._models = models

        return self

    def update(self):
        raise NotImplementedError

    def where(self):
        raise NotImplementedError

    def result(self):
        raise NotImplementedError
