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
    NamedTuple,
    Optional,
    Tuple,
    Type,
    Union,
)

from .comparisons import Comparison, Equal
from .models import Edge, Node


# User | user
NodeUnit = Union[Node, Type[Node]]
# User | (User, 'a') | user | (user, 'a')
NodeUnitOrTuple = Union[NodeUnit, Tuple[NodeUnit, str]]
# Knows | knows
EdgeUnit = Union[Edge, Type[Edge]]
# Knows | (Knows, 'a') | knows | (knows, 'a')
EdgeUnitOrTuple = Union[EdgeUnit, Tuple[EdgeUnit, str]]
# user | knows
ModelInstance = Union[Edge, Node]
# User | Knows
ModelType = Type[Union[Edge, Node]]
# user | (user, 'a') | knows | (knows, 'a')
InstanceOrTuple = Union[ModelInstance, Tuple[ModelInstance, str]]
# User | (User, 'a') | Knows | (Knows, 'a')
TypeOrTuple = Union[ModelType, Tuple[ModelType, str]]
# user | (user, 'a') | knows | (knows, 'a') | User | (User, 'a') | Knows | ...
UnitOrTuple = Union[InstanceOrTuple, TypeOrTuple]


class ModelDetails(NamedTuple):
    """
    Organized details of a UnitOrTuple.
    """
    model: ModelType
    var: str
    instance: Optional[ModelInstance]
    start: Optional[str]
    end: Optional[str]


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
            model_by_var: MutableMapping[str, ModelType],
            var_by_model: MutableMapping[ModelType, str],
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
            model_by_var: MutableMapping[str, ModelType],
            var_by_model: MutableMapping[ModelType, str],
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
        self.model_by_var: MutableMapping[str, ModelType] = {}
        self.var_by_model: MutableMapping[ModelType, str] = {}
        self.return_order = []
        self.chains: List[Chain] = []
        self.generator = generate_variables()
        self.model: ModelType = None

    def _get_details(self, data: UnitOrTuple) -> ModelDetails:
        """
        Convert a UnitOrTuple into ModelDetails.
        """
        if isinstance(data, tuple):
            instance_or_type, variable = (data[0], '_' + data[1])
        else:
            instance_or_type, variable = data, next(self.generator)

        if isinstance(instance_or_type, (Node, Edge)):
            instance = instance_or_type
            model = type(instance_or_type)
        else:
            instance = None
            model = instance_or_type

        if isinstance(instance, Edge):
            raise NotImplementedError
        else:
            start = None
            end = None

        # pylint: disable=too-many-function-args
        return ModelDetails(model, variable, instance, start, end)

    # def create(self, *instances: ModelInstance) -> 'Query':
    #     """
    #     Schedule models for creation.
    #
    #     :param instances: models to create
    #     :return: self
    #     """
    #     raise NotImplementedError
    #
    # def update(self, *models: ModelInstance) -> 'Query':
    #     """
    #     Schedule models for update.
    #
    #     :param models: models to update
    #     :return: self
    #     """
    #     raise NotImplementedError

    def match(self, node: NodeUnitOrTuple, *where: Callable) -> 'Query':
        """
        Set the starting node to the cypher `MATCH` query.

        :param node: node to match
        :param where: conditions for the `node` to match
        :return: self
        """
        chain = MatchingChain(self.model_by_var, self.var_by_model)
        self.chains.append(chain)

        details = self._get_details(node)
        chain.add_node(details.model)
        self.model = details.model
        if details.instance:
            uid = details.instance.uid
            chain.add_comparison(Equal(details.model, details.var, 'uid', uid))

        for condition in where:
            chain.add_comparison(condition(self.model, details.var))

        self.model_by_var[details.var] = details.model
        self.var_by_model[details.model] = details.var
        self.return_order.append(details.var)

        return self

    def connected_through(
            self,
            edge: EdgeUnitOrTuple,
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
    def to(self, node: NodeUnitOrTuple, *where: Comparison) -> 'Query':
        """
        Add the right node to the `-[]->` connection in the cypher query.

        :param node: node to match
        :param where: conditions for the `node` to match
        :return: self
        """
        raise NotImplementedError

    # pylint: disable=invalid-name
    def by(self, node: NodeUnitOrTuple, *where: Comparison) -> 'Query':
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
