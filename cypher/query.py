"""
Cypher query builder.
"""
import enum
import itertools
import string
from collections import OrderedDict
from typing import (
    Callable,
    Generator,
    Iterable,
    Mapping,
    MutableMapping,
    List,
    Optional,
    MutableSet,
    Tuple,
    Type,
    Union,
)

from .models import Edge, ModelDetails, Node
from .props import BaseProp


Model = Union[Edge, Node]
Identifier = Union[Model, Type[Model]]
Comparison = Callable[[ModelDetails, BaseProp], str]


def generate_paths() -> Generator[str, None, None]:
    """
    Generate path variables: "_p1", "_p2", "_p3", ...

    :return: generator of path variables
    """
    for i in itertools.count(1):
        yield '_p' + str(i)


def generate_variables() -> Generator[str, None, None]:
    """
    Generate variables: "_a", "_b", ..., "_z", "_aa", "_ab", ...
    Non of variables should start with "_p".

    :return: generator of variables
    """
    for i in itertools.count(1):
        for letters in itertools.product(string.ascii_lowercase, repeat=i):
            if not letters[0] == 'p':
                yield '_' + ''.join(letters)


class Direction(enum.Enum):
    """
    Directions of edges in cypher patterns.
    """
    NONE = enum.auto()
    BACK = enum.auto()
    FRONT = enum.auto()


class Chain:
    """
    Base class for all chains.
    """
    def __init__(
            self,
            details: Mapping[str, ModelDetails],
            defined: MutableSet,
    ):
        self.details = details
        self.defined = defined
        self.elements: List[str] = []


class MatchingChain(Chain):
    """
    Matching chain builder.
    """
    def __init__(self, details, defined):
        super().__init__(details, defined)

        self.directions: List[Direction] = []
        self.paths: List[str] = []
        self.conditions: List[str] = []

    def _check_pattern_integrity(self):
        """
        Check if the pattern is valid.
        """

    def _add_instance_filter(self, model: ModelDetails):
        """
        Add filtering by `primary_key`.
        """
        prop_name = model.type.Meta.primary_key
        prop = getattr(model.type, prop_name)
        value = getattr(model.instance, prop_name)
        self.add_condition(prop == value)

    def add_node(self, var: str, direction: Direction = None):
        """
        Add a node to the matching pattern.
        """
        self.elements.append(var)
        if direction is not None:
            self.directions.append(direction)

        model = self.details[var]
        if model.instance is not None:
            self._add_instance_filter(model)

        self._check_pattern_integrity()

    def add_edge(self, var: str, path: str):
        """
        Add an edge to the matching pattern.
        """
        self.elements.append(var)
        self.paths.append(path)

        model = self.details[var]
        if model.instance is not None:
            self._add_instance_filter(model)

        self._check_pattern_integrity()

    def add_condition(self, comparison):
        """
        Add a condition to the query.
        """
        self.conditions.append(comparison(self.details, self.elements[-1]))

    def __str__(self) -> str:
        """
        Stringify the chain.
        """
        if len(self.elements) == 1:
            element = self.elements[0]
            self.defined.add(element)

            query = 'MATCH (%s)' % self.details[element].get_var_and_labels()
        else:
            paths = []
            for i in range(len(self.paths)):
                if self.elements[i * 2] in self.defined:
                    start = self.elements[i * 2]
                else:
                    start_details = self.details[self.elements[i * 2]]
                    start = start_details.get_var_and_labels()
                    self.defined.add(start_details.var)

                if self.elements[i * 2 + 2] in self.defined:
                    end = self.elements[i * 2 + 2]
                else:
                    end_details = self.details[self.elements[i * 2 + 2]]
                    end = end_details.get_var_and_labels()
                    self.defined.add(end_details.var)

                edge_details = self.details[self.elements[i * 2 + 1]]
                self.defined.add(edge_details.var)

                if edge_details.conn is None:
                    edge = edge_details.get_var_and_labels()
                    rels_var = ''
                else:
                    if edge_details.conn == (None, None):
                        length = '*'
                    else:
                        length = '*{}..{}'.format(
                            edge_details.conn[0] or '',
                            edge_details.conn[1] or '',
                        )

                    label = ':'.join(('', *edge_details.get_labels()))
                    edge = ' '.join((label, length)).strip()
                    # noinspection SqlNoDataSourceInspection
                    rels_var = '\nWITH *, relationships(%s) as %s' % (
                        self.paths[i],
                        edge_details.var,
                    )

                paths.append('MATCH %s = (%s)%s-[%s]-%s(%s)%s' % (
                    self.paths[i],
                    start,
                    '<' if self.directions[i] == Direction.BACK else '',
                    edge,
                    '>' if self.directions[i] == Direction.FRONT else '',
                    end,
                    rels_var,
                ))
            query = '\n'.join(paths)

        if self.conditions:
            conditions = '\nWHERE ' + '\n  AND '.join(self.conditions)
            query += conditions

        return query


class Query:
    """
    Cypher query builder.
    """
    def __init__(self):
        self.var_generator = generate_variables()
        self.path_generator = generate_paths()
        self.chains: List[Chain] = []
        self.details: MutableMapping[str, ModelDetails] = {}
        self.defined: MutableSet = set()
        self.output: List[str] = []

    def _add_details(
            self,
            identifier: Identifier,
            var: Optional[str],
            conn: Tuple[Optional[int], Optional[int]] = None,
    ) -> str:
        """
        Generate a variable if needed and add a ModelDetails instance to
        `details` property.
        """
        var = var or next(self.var_generator)
        self.details[var] = ModelDetails(identifier, var, conn)

        return var

    def match(
            self,
            identifier: Union[Type[Node], Node, None],
            var: str = None,
    ) -> 'Query':
        """
        Start a `MatchingChain`.
        """
        var = self._add_details(identifier or Node, var)
        self.output.append(var)

        chain = MatchingChain(self.details, self.defined)
        chain.add_node(var)
        self.chains.append(chain)

        return self

    def connected_through(
            self,
            identifier: Union[Type[Edge], Edge, None],
            var: str = None,
            conn: Tuple[Optional[int], Optional[int]] = None,
    ) -> 'Query':
        """
        Add an Edge to the `MatchingChain`.
        """
        var = self._add_details(identifier or Edge, var, conn)
        self.output.append(var)

        chain: MatchingChain = self.chains[-1]
        chain.add_edge(var, next(self.path_generator))

        return self

    def _by_to_with(
            self,
            direction: Direction,
            identifier: Union[Type[Node], Node, None],
            var: str = None,
    ) -> 'Query':
        var = self._add_details(identifier or Node, var)
        self.output.append(var)

        chain: MatchingChain = self.chains[-1]
        chain.add_node(var, direction)

        return self

    def with_(
            self,
            identifier: Union[Type[Node], Node, None],
            var: str = None,
    ) -> 'Query':
        """
        Add a Node to the `MatchingChain`. Direction undefined.
        """
        return self._by_to_with(Direction.NONE, identifier, var)

    def by(
            self,
            identifier: Union[Type[Node], Node, None],
            var: str = None,
    ) -> 'Query':
        """
        Add a Node to the `MatchingChain`. Direction: back.
        """
        # pylint: disable=invalid-name
        # This suppresses error for the method name.
        # pylint: enable=no-member
        return self._by_to_with(Direction.BACK, identifier, var)

    def to(
            self,
            identifier: Union[Type[Node], Node, None],
            var: str = None,
    ) -> 'Query':
        """
        Add a Node to the `MatchingChain`. Direction: front.
        """
        # pylint: disable=invalid-name
        # This suppresses error for the method name.
        # pylint: enable=no-member
        return self._by_to_with(Direction.FRONT, identifier, var)

    def _by_to_with_var(
            self,
            direction: Direction,
            var: str = None,
    ) -> 'Query':
        chain: MatchingChain = self.chains[-1]
        chain.add_node(var, direction)

        return self

    def with_var(
            self,
            var: str = None,
    ) -> 'Query':
        """
        Add a Node by variable to the `MatchingChain`. Direction undefined.
        """
        return self._by_to_with_var(Direction.NONE, var)

    def by_var(
            self,
            var: str = None,
    ) -> 'Query':
        """
        Add a Node by variable to the `MatchingChain`. Direction: back.
        """
        return self._by_to_with_var(Direction.BACK, var)

    def to_var(
            self,
            var: str = None,
    ) -> 'Query':
        """
        Add a Node by variable to the `MatchingChain`. Direction: front.
        """
        return self._by_to_with_var(Direction.FRONT, var)

    def where(self, *comparisons: Comparison) -> 'Query':
        """
        Add a condition to the matching chain.
        """
        chain: MatchingChain = self.chains[-1]
        for comparison in comparisons:
            chain.add_condition(comparison)

        return self

    def result(
            self,
            *output,
            no_exec: bool = False,
    ) -> Iterable:
        """
        Execute the query and map the results.
        """
        output = output or OrderedDict.fromkeys(self.output).keys()
        result = 'RETURN %s' % ', '.join(output)
        query = '\n'.join((*map(str, self.chains), result))

        if no_exec:
            return query
        raise NotImplementedError


# import enum
# import itertools
# import string
# from collections import OrderedDict
# from typing import (
#     Callable,
#     Generator,
#     Iterable,
#     List,
#     MutableMapping,
#     NamedTuple,
#     Optional,
#     Tuple,
#     Type,
#     Union,
# )
#
# from .comparisons import Comparison, Equal
# from .models import Edge, Node
#
#
# # User | user
# NodeUnit = Union[Node, Type[Node], None]
# # User | (User, 'a') | user | (user, 'a') | None | (None, 'a')
# NodeUnitOrTuple = Union[NodeUnit, Tuple[NodeUnit, str]]
# # Knows | knows
# EdgeUnit = Union[Edge, Type[Edge], None]
# # Knows | (Knows, 'a') | knows | (knows, 'a') | None | (None, 'a')
# EdgeUnitOrTuple = Union[EdgeUnit, Tuple[EdgeUnit, str]]
# # user | knows
# ModelInstance = Union[Edge, Node]
# # User | Knows
# ModelType = Type[Union[Edge, Node]]
# # user | (user, 'a') | knows | (knows, 'a')
# InstanceOrTuple = Union[ModelInstance, Tuple[ModelInstance, str]]
# # User | (User, 'a') | Knows | (Knows, 'a')
# TypeOrTuple = Union[ModelType, Tuple[ModelType, str]]
# # user | (user, 'a') | knows | (knows, 'a') | User | (User, 'a') | Knows | ...
# UnitOrTuple = Union[InstanceOrTuple, TypeOrTuple]
#
#
# def not_impl():
#     """
#     Only for dev development.
#
#     :raise: NotImplementedError
#     """
#     raise NotImplementedError('this is still to be developed')
#
#
# def generate_paths() -> Generator[str, None, None]:
#     """
#     Generate path variables: "_p1", "_p2", "_p3", ...
#
#     :return: generator of path variables
#     """
#     for i in itertools.count(1):
#         yield '_p' + str(i)
#
#
# def generate_variables() -> Generator[str, None, None]:
#     """
#     Generate variables: "_a", "_b", ..., "_z", "_aa", "_ab", ...
#     Non of variables should start with "_p".
#
#     :return: generator of variables
#     """
#     for i in itertools.count(1):
#         for letters in itertools.product(string.ascii_lowercase, repeat=i):
#             if not letters[0] == 'p':
#                 yield '_' + ''.join(letters)
#
#
# class ModelDetails(NamedTuple):
#     """
#     Organized details of a UnitOrTuple.
#     """
#     var: str
#     model: Optional[ModelType]
#     instance: Optional[ModelInstance]
#     start: Optional[str]
#     end: Optional[str]
#     conn: Optional[Tuple[Optional[int], Optional[int]]]
#
#     def get_labels(self) -> Tuple[str, ...]:
#         """
#         :return: sorted tuple of labels
#         """
#         if self.instance:
#             return tuple(sorted(self.instance.labels))
#
#         if self.model:
#             return self.model.__name__,
#
#         return ()
#
#     def get_var_and_labels(self) -> str:
#         """
#         Get a string ready to be used in cypher pattern.
#         Example: `a:Human:Person`.
#         """
#         return ':'.join((self.var, *self.get_labels()))
#
#
# class Outcome(NamedTuple):
#     """
#     Wrapper for the Query outcome elements.
#     """
#     result: str
#     mapper: Callable
#
#
# class Direction(enum.Enum):
#     """
#     Directions of edges in cypher patterns.
#     """
#     NONE = enum.auto()
#     BACK = enum.auto()
#     FRONT = enum.auto()
#
#
# class Chain:
#     """
#     Base class for all chains.
#     """
#     def __init__(
#             self,
#             model_details: MutableMapping[str, ModelType],
#     ):
#         """
#         :param model_details: dictionary with variables as keys
#         """
#         self.model_details = model_details
#
#     def stringify(self) -> str:
#         """
#         :return: chain as string for cypher query
#         """
#         raise NotImplementedError
#
#
# class MatchingChain(Chain):
#     """
#     Matching chain for query.
#     """
#     def __init__(
#             self,
#             model_details: MutableMapping[str, ModelType],
#     ):
#         """
#         :param model_details: dictionary with variables as keys
#         """
#         super().__init__(model_details)
#         self.comparisons: List[Comparison] = []
#         self.models: List[ModelDetails] = []
#         self.directions: List[Direction] = []
#         self.paths: List[str] = []
#
#     def add_node(self, details: ModelDetails):
#         """
#         Add node to pattern.
#
#         :param details: details of the node to add
#         """
#         self.models.append(details)
#
#     def add_edge(self, details: ModelDetails):
#         """
#         Add edge to pattern.
#
#         :param details: details of the edge to add
#         """
#         self.models.append(details)
#
#     def add_path(self, path: str):
#         """
#         Add path name.
#         """
#         self.paths.append(path)
#
#     def add_direction(self, direction: Direction):
#         """
#         Add direction to the edge in pattern.
#
#         :param direction: direction of the connection
#         """
#         self.directions.append(direction)
#
#     def add_conditions(
#             self,
#             details: ModelDetails,
#             conditions: Iterable[Callable],
#     ):
#         """
#         Add `WHERE` comparisons to the chain.
#
#         :param details: details of the matching model
#         :param conditions: conditions to meet
#         """
#         if details.instance:
#             uid = details.instance.uid
#             uid_equality = Equal(details.model, details.var, 'uid', uid)
#             self.comparisons.append(uid_equality)
#
#         for condition in conditions:
#             self.comparisons.append(condition(details.model, details.var))
#
#     def stringify(self) -> str:
#         """
#         :return: chain as part of cypher query
#         """
#         if len(self.models) == 1:
#             details = self.models[0]
#             lines = ['MATCH ({})'.format(details.get_var_and_labels())]
#         else:
#             pattern = (
#                 'MATCH {path} = '
#                 '({start}){left}-[{edge}{conn}]-{right}({end}){rels}'
#             )
#             lines = []
#             for i in range(len(self.models) // 2):
#                 model = self.models[i * 2]
#                 start = model.get_var_and_labels() if i == 0 else model.var
#
#                 model = self.models[i * 2 + 1]
#                 if model.conn:
#                     edge = ':'.join(('', *model.get_labels()))
#                     conn = ' *{}..{}'.format(*(
#                         str(num) if num is not None else ''
#                         for num in model.conn
#                     ))
#                     rels = '\nWITH *, relationships({}) as {}'.format(
#                         self.paths[i], model.var
#                     )
#                 else:
#                     edge = model.get_var_and_labels()
#                     conn = ''
#                     rels = ''
#
#                 lines.append(pattern.format(
#                     path=self.paths[i],
#                     start=start,
#                     left='<' if self.directions[i] == Direction.BACK else '',
#                     edge=edge,
#                     conn=conn,
#                     right='>' if self.directions[i] == Direction.FRONT else '',
#                     end=self.models[i * 2 + 2].get_var_and_labels(),
#                     rels=rels
#                 ))
#         result = '\n'.join(lines)
#
#         if self.comparisons:
#             result += '\nWHERE ' + '\n  AND '.join(
#                 condition.stringify() for condition in self.comparisons
#             )
#
#         return result
#
#
# class Query:
#     """
#     Cypher query builder.
#     """
#     def __init__(self):
#         """
#         Instantiate a new query object.
#         """
#         self.model_details: MutableMapping[str, ModelType] = {}
#         self.outcome: OrderedDict = OrderedDict()
#         self.chains: List[Chain] = []
#
#         self.path_generator = generate_paths()
#         self.vars_generator = generate_variables()
#
#     def _get_details(
#             self,
#             data: UnitOrTuple,
#             conn: Optional[Tuple[Optional[int], Optional[int]]] = None,
#     ) -> ModelDetails:
#         """
#         Convert a UnitOrTuple into ModelDetails.
#         """
#         if isinstance(data, tuple):
#             instance_or_type, variable = data
#         else:
#             instance_or_type, variable = data, next(self.vars_generator)
#
#         if isinstance(instance_or_type, (Node, Edge)):
#             instance = instance_or_type
#             model = type(instance_or_type)
#         else:
#             instance = None
#             model = instance_or_type
#
#         if isinstance(instance, Edge):
#             # This will be changed when it comes to the `create` action.
#             start = None
#             end = None
#         else:
#             start = None
#             end = None
#
#         # pylint: disable=too-many-function-args
#         return ModelDetails(variable, model, instance, start, end, conn)
#
#     def match(self, node: NodeUnitOrTuple, *where: Callable) -> 'Query':
#         """
#         Set the starting node to the cypher `MATCH` query.
#
#         :param node: node to match
#         :param where: conditions for the `node` to match
#         :return: self
#         """
#         chain = MatchingChain(self.model_details)
#         self.chains.append(chain)
#
#         details = self._get_details(node)
#         chain.add_node(details)
#         chain.add_conditions(details, where)
#
#         self.model_details[details.var] = details.model
#         self.outcome[details.var] = Outcome(details.var, not_impl)
#
#         return self
#
#     def connected_through(
#             self,
#             edge: EdgeUnitOrTuple,
#             *where: Callable,
#             conn: Tuple[Optional[int], Optional[int]] = None,
#     ) -> 'Query':
#         """
#         Add a connection to the matching chain.
#
#         :param edge: edge to match
#         :param where: conditions to meet
#         :param conn: range of connections between nodes
#         :return: self
#         """
#         chain: MatchingChain = self.chains[-1]
#
#         details = self._get_details(edge, conn)
#         path = next(self.path_generator)
#         chain.add_edge(details)
#         chain.add_path(path)
#         chain.add_conditions(details, where)
#
#         self.model_details[details.var] = details.model
#         self.outcome[details.var] = Outcome(details.var, not_impl)
#
#         return self
#
#     def _by_to_with(
#             self,
#             direction: Direction,
#             node: NodeUnitOrTuple,
#             *where: Callable,
#     ) -> 'Query':
#         """
#         Common logic for `to`, `by` and `with_` methods.
#
#         :param direction: direction of connection
#         :param node: node to add
#         :param where: conditions to meet
#         :return: self
#         """
#         chain: MatchingChain = self.chains[-1]
#
#         details = self._get_details(node)
#         chain.add_edge(details)
#         chain.add_direction(direction)
#         chain.add_conditions(details, where)
#
#         self.model_details[details.var] = details.model
#         self.outcome[details.var] = Outcome(details.var, not_impl)
#
#         return self
#
#     def with_(self, node: NodeUnitOrTuple, *where: Callable) -> 'Query':
#         """
#         Add a node after connection with no direction to the matching chain.
#
#         :param node: node to add
#         :param where: conditions to meet
#         :return: self
#         """
#         return self._by_to_with(Direction.NONE, node, *where)
#
#     def by(self, node: NodeUnitOrTuple, *where: Callable) -> 'Query':
#         """
#         Add a node after connection with back direction to the matching chain.
#
#         :param node: node to add
#         :param where: conditions to meet
#         :return: self
#         """
#         # pylint: disable=invalid-name
#         # This suppresses error for the method name.
#         # pylint: enable=no-member
#         return self._by_to_with(Direction.BACK, node, *where)
#
#     def to(self, node: NodeUnitOrTuple, *where: Callable) -> 'Query':
#         """
#         Add a node after connection with front direction to the matching chain.
#
#         :param node: node to add
#         :param where: conditions to meet
#         :return: self
#         """
#         # pylint: disable=invalid-name
#         # This suppresses error for the method name.
#         # pylint: enable=no-member
#         return self._by_to_with(Direction.FRONT, node, *where)
#
#     def result(
#             self,
#             *variables: str,
#             # distinct: bool = False,
#             # limit: int = None,
#             # skip: int = None,
#             # order_by: str = None,
#             # transaction: None = None,  # should be with __enter__ and __exit__
#             no_exec: bool = False,
#     ) -> Iterable:
#         """
#         Execute the query and map the results.
#
#         # :param variables: data to return
#         # :param distinct: add `DISTINCT` to the query
#         # :param limit: limit the number of results
#         # :param skip: skip a number of results
#         # :param order_by: add ordering
#         # :param transaction: transaction in which to perform the query
#         :param no_exec: return query without hitting the database
#         :return: result of the query mapped by appropriate types
#         """
#         if variables:
#             returns = map(lambda var: self.outcome[var].result, variables)
#         else:
#             returns = map(lambda elem: elem.result, self.outcome.values())
#
#         command = '\n'.join((
#             *(chain.stringify() for chain in self.chains),
#             'RETURN ' + ', '.join(returns),
#         ))
#
#         if no_exec:
#             return command
#         raise NotImplementedError
