from enum import Enum, auto
from typing import Iterable, List, Tuple, Type, Union

from .comparisons import Comparison
from .models import Edge, Model, Node
from .props import BaseProp


ModelInstance = Union[
    Union[Edge, Node],
    Tuple[Union[Edge, Node], str],
]
ModelUnit = Union[
    ModelInstance,
    Tuple[Model, str],
    Tuple[Type[Model], str],
]
EdgeUnit = Union[
    Edge,
    Type[Edge],
    Tuple[Edge, str],
    Tuple[Type[Edge], str],
]
NodeUnit = Union[
    Node,
    Type[Node],
    Tuple[Node, str],
    Tuple[Type[Node], str],
]


class Orders:
    CREATE = auto()
    MATCH = auto()
    MERGE = auto()


class Action:
    def __init__(
        self,
        action: auto,
        model: Union[Edge, Node, Type[Union[Edge, Node]]],
        variable: str=None,
    ):
        is_type = issubclass(model, (Edge, Node))

        self.action = action
        self.model = model if is_type else type(model)
        self.instance = None if is_type else model
        self.variable = variable

        if action == Orders.CREATE and self.instance is None:
            assert False  # @TODO: raise some nice exception


class Query:
    """
    Cypher query builder.
    """
    def __init__(self):
        self.actions: List[Action] = []

    @staticmethod
    def represent(model: Union[Edge, Node]) -> str:
        """
        Stringify a model.

        :param model: model to stringify
        :return: cypher representation
        """
        cls = type(model)
        label = cls.__name__
        props = []
        for name in sorted(dir(cls)):
            prop_type = getattr(cls, name)

            if isinstance(prop_type, BaseProp):
                value = getattr(model, name)
                if value is not None:
                    props.append((name, prop_type.to_cypher_value(value)))

        return ':%s {%s}' % (
            label,
            ', '.join(map(lambda pair: ': '.join(pair), props)),
        )

    def create(self, *instances: ModelInstance) -> 'Query':
        """
        Schedule models for creation.

        :param instances: models to create
        :return: self
        """
        for instance in instances:
            if isinstance(instance, tuple):
                self.actions.append(Action(Orders.CREATE, *instance))
            else:
                self.actions.append(Action(Orders.CREATE, instance))

        return self

    def update(self, *models: ModelInstance) -> 'Query':
        """
        Schedule models for update.

        :param models: models to update
        :return: self
        """
        raise NotImplementedError

    def match(self, node: NodeUnit, *where: Comparison) -> 'Query':
        """
        Set the starting node to the cypher `MATCH` query.

        :param node: node to match
        :param where: conditions for the `node` to match
        :return: self
        """
        raise NotImplementedError

    def match_or_create(self, node: NodeUnit, *where: Comparison) -> 'Query':
        """
        Set the starting node to the cypher `MERGE` query.

        :param node: node to match
        :param where: conditions for the `node` to match
        :return: self
        """
        raise NotImplementedError

    def connected_through(self, edge: EdgeUnit, *where: Comparison) -> 'Query':
        """
        Add an edge to the cypher query.

        :param edge: edge to match
        :param where: conditions for the `edge` to match
        :return: self
        """
        raise NotImplementedError

    def to(self, node: NodeUnit, *where: Comparison) -> 'Query':
        """
        Add the right node to the `-[]->` connection in the cypher query.

        :param node: node to match
        :param where: conditions for the `node` to match
        :return: self
        """
        raise NotImplementedError

    def by(self, node: NodeUnit, *where: Comparison) -> 'Query':
        """
        Add the right node to the `<-[]-` connection in the cypher query.

        :param node: node to match
        :param where: conditions for the `node` to match
        :return: self
        """
        raise NotImplementedError

    def where(self, *conditions: Comparison) -> 'Query':
        """
        Add arbitrary conditions.

        :param conditions: conditions to meet
        :return: self
        """
        raise NotImplementedError

    def delete(self, *variables: str) -> dict:
        """
        Schedule the models represented by the listed variables for deletion.

        :param variables: models to delete
        :return: self
        """
        # return tx.run(query).summary().counters
        raise NotImplementedError

    def result(
        self,
        *variables: str,
        distinct: bool=False,
        limit: int=None,
        skip: int=None,
        order_by: str=None,
        transaction: None=None,  # should be with __enter__ and __exit__
        no_exec: bool=False,
    ) -> Iterable:
        """
        Execute the query and map the results.
        
        :param variables: data to return
        :param distinct: add `DISTINCT` to the query
        :param limit: limit the number of results
        :param skip: skip a number of results
        :param order_by: add ordering
        :param transaction: transaction in which to perform the query
        :param no_exec: return query without hitting the database
        :return: result of the query mapped by appropriate types
        """
        # import itertools
        #
        # action_type = None
        # action_index = 0
        # query = []
        #
        # while True:
        #     try:
        #         action_type = self.actions[action_index].action
        #     except IndexError:
        #         break
        #
        #     actions = tuple(itertools.takewhile(
        #         lambda a: a.action == action_type,
        #         self.actions[action_index:],
        #     ))
        #     action_index += len(actions)
        #
        #     # if action_type == Orders.CREATE:
        #
        # if no_exec:
        #     return ''.join(query)
        raise NotImplementedError
