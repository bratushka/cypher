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
NodeUnit = Union[Node, Type[Node], None]
# User | (User, 'a') | user | (user, 'a') | None | (None, 'a')
NodeUnitOrTuple = Union[NodeUnit, Tuple[NodeUnit, str]]
# Knows | knows
EdgeUnit = Union[Edge, Type[Edge], None]
# Knows | (Knows, 'a') | knows | (knows, 'a') | None | (None, 'a')
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
    var: str
    model: Optional[ModelType]
    instance: Optional[ModelInstance]
    start: Optional[str]
    end: Optional[str]

    def get_labels(self) -> Tuple[str, ...]:
        """
        :return: sorted tuple of labels
        """
        if self.instance:
            return tuple(sorted(self.instance.labels))

        if self.model:
            return self.model.__name__,

        return ()


def generate_variables() -> Generator[str, None, None]:
    """
    Generate variables: "_a", "_b", ..., "_z", "_aa", "_ab", ...

    :return: generator of variables
    """
    for i in itertools.count(1):
        for letters in itertools.product(string.ascii_lowercase, repeat=i):
            yield '_' + ''.join(letters)


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
            model_details: MutableMapping[str, ModelType],
    ):
        """
        :param model_details: dictionary with variables as keys
        """
        self.model_details = model_details

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
            model_details: MutableMapping[str, ModelType],
    ):
        """
        :param model_details: dictionary with variables as keys
        """
        super().__init__(model_details)
        self.comparisons: List[Comparison] = []
        self.models: List[ModelDetails] = []
        self.directions: List[Direction] = []

    def add_node(self, details: ModelDetails):
        """
        Add node to pattern.

        :param details: details of the node to add
        """
        self.models.append(details)

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
            ':'.join((details.var, *details.get_labels()))
            for details in self.models
        ))

        if self.comparisons:
            result += '\nWHERE ' + '\n  AND '.join(
                # pylint: disable=no-member
                condition.stringify() for condition in self.comparisons
            )

        return result


class Query:
    """
    Cypher query builder.
    """
    def __init__(self):
        """
        Instantiate a new query object.
        """
        self.model_details: MutableMapping[str, ModelType] = {}
        self.return_order = []
        self.chains: List[Chain] = []
        self.generator = generate_variables()

    def _get_details(self, data: UnitOrTuple) -> ModelDetails:
        """
        Convert a UnitOrTuple into ModelDetails.
        """
        if isinstance(data, tuple):
            instance_or_type, variable = data
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
        return ModelDetails(variable, model, instance, start, end)

    def match(self, node: NodeUnitOrTuple, *where: Callable) -> 'Query':
        """
        Set the starting node to the cypher `MATCH` query.

        :param node: node to match
        :param where: conditions for the `node` to match
        :return: self
        """
        chain = MatchingChain(self.model_details)
        self.chains.append(chain)

        details = self._get_details(node)
        chain.add_node(details)

        if details.instance:
            uid = details.instance.uid
            chain.add_comparison(Equal(details.model, details.var, 'uid', uid))

        for condition in where:
            chain.add_comparison(condition(details.model, details.var))

        self.model_details[details.var] = details.model
        self.return_order.append(details.var)

        return self

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
