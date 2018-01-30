"""
Cypher query builder.
"""
import enum
import itertools
import string
from typing import (
    Callable,
    Generator,
    Iterable,
    List,
    MutableMapping,
    Tuple,
    Type,
    Union,
)

from .comparisons import Comparison, Equal
from .models import Edge, Model, Node


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
ModelType = Type[Union[Edge, Node]]


def generate_variables() -> Generator[str, None, None]:
    """
    Generate variables: "a", "b", ..., "z", "aa", "ab", ...

    :return: generator of variables
    """
    for i in itertools.count(1):
        for letters in itertools.product(string.ascii_lowercase, repeat=i):
            yield ''.join(letters)


class Direction(enum.Enum):
    """
    Directions of edges in cypher patterns.
    """
    LEFT = enum.auto()
    RIGHT = enum.auto()


class Chain:
    """
    Base class for all chains.
    """
    def __init__(
            self,
            model_by_var: MutableMapping[str, Model],
            var_by_model: MutableMapping[Model, str],
    ):
        """
        :param model_by_var: dictionary with models as keys
        :param var_by_model: dictionary with variables as keys
        """
        self.model_by_var = model_by_var
        self.var_by_model = var_by_model

    def stringify(self) -> str:
        """
        :return: chain as string for cypher query
        """
        raise NotImplementedError


class MatchingChain(Chain):
    """
    Matching chain for query.
    """
    def __init__(
            self,
            model_by_var: MutableMapping[str, Model],
            var_by_model: MutableMapping[Model, str],
    ):
        """
        :param model_by_var: dictionary with models as keys
        :param var_by_model: dictionary with variables as keys
        """
        super().__init__(model_by_var, var_by_model)
        self.comparisons: List[Comparison] = []
        self.models: List[ModelType] = []
        self.directions: List[Direction] = []

    def add_node(self, node: Type[Node]):
        """
        Add node to pattern.

        :param node: node to add
        """
        self.models.append(node)

    def add_comparison(self, comparison: Comparison):
        """
        Add `WHERE` condition.

        :param comparison: Comparison object
        """
        self.comparisons.append(comparison)

    def stringify(self) -> str:
        """
        :return: chain as part of cypher query
        """
        pattern = ['({})']

        for i in range(len(self.models[1::2])):
            pattern.append('{}-[{{}}]-{}({{}})'.format(
                self.directions[i] == Direction.LEFT,
                self.directions[i] == Direction.RIGHT,
            ))

        result = 'MATCH ' + ''.join(pattern).format(*(
            ''.join((self.var_by_model[model], ':', model.__name__))
            for model in self.models
        ))

        if self.comparisons:
            result += '\nWHERE ' + '\n  AND '.join(
                # pylint: disable=no-member
                condition.stringify() for condition in self.comparisons
            )

        return result


# class CreateChain(Chain):
#     pass
#
#
# class UpdateChain(Chain):
#     pass


class Query:
    """
    Cypher query builder.
    """
    def __init__(self):
        """
        Instantiate a new query object.
        """
        self.model_by_var: MutableMapping[str, Model] = {}
        self.var_by_model: MutableMapping[Model, str] = {}
        self.return_order = []
        self.chains: List[Chain] = []
        self.generator = generate_variables()
        self.model: ModelType = None

    def create(self, *instances: ModelInstance) -> 'Query':
        """
        Schedule models for creation.

        :param instances: models to create
        :return: self
        """
        raise NotImplementedError

    def update(self, *models: ModelInstance) -> 'Query':
        """
        Schedule models for update.

        :param models: models to update
        :return: self
        """
        raise NotImplementedError

    def match(self, node: NodeUnit, *where: Callable) -> 'Query':
        """
        Set the starting node to the cypher `MATCH` query.

        :param node: node to match
        :param where: conditions for the `node` to match
        :return: self
        """
        chain = MatchingChain(self.model_by_var, self.var_by_model)
        self.chains.append(chain)

        # @TODO: export to a separate method everything from here...
        if isinstance(node, tuple):
            variable = '_' + node[1]
            node = node[0]
        else:
            variable = next(self.generator)

        if isinstance(node, Node):
            uid = node.uid
            node = type(node)
            chain.add_comparison(Equal(node, variable, 'uid', uid))
        chain.add_node(node)
        # ... to here
        self.model = node

        for condition in where:
            chain.add_comparison(condition(self.model, variable))

        self.model_by_var[variable] = node
        self.var_by_model[node] = variable
        self.return_order.append(variable)

        return self

    def connected_through(
            self,
            edge: EdgeUnit,
            *where: Comparison,
            min_connections: int = 1,
            max_connections: int = 1,
    ) -> 'Query':
        """
        Add an edge to the cypher query.

        :param edge: edge to match
        :param where: conditions for the `edge` to match
        :param min_connections: minimum connection length
        :param max_connections: maximum connection length
        :return: self
        """
        raise NotImplementedError

    # pylint: disable=invalid-name
    def to(self, node: NodeUnit, *where: Comparison) -> 'Query':
        """
        Add the right node to the `-[]->` connection in the cypher query.

        :param node: node to match
        :param where: conditions for the `node` to match
        :return: self
        """
        raise NotImplementedError

    # pylint: disable=invalid-name
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
            # *variables: str,
            # distinct: bool = False,
            # limit: int = None,
            # skip: int = None,
            # order_by: str = None,
            # transaction: None = None,  # should be with __enter__ and __exit__
            no_exec: bool = False,
    ) -> Iterable:
        """
        Execute the query and map the results.

        # :param variables: data to return
        # :param distinct: add `DISTINCT` to the query
        # :param limit: limit the number of results
        # :param skip: skip a number of results
        # :param order_by: add ordering
        # :param transaction: transaction in which to perform the query
        :param no_exec: return query without hitting the database
        :return: result of the query mapped by appropriate types
        """
        command = '\n'.join((
            *(chain.stringify() for chain in self.chains),
            'RETURN ' + ', '.join(self.return_order),
        ))

        if no_exec:
            return command
        raise NotImplementedError
