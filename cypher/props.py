"""
Properties for models.
"""
import json
from datetime import date, datetime
from math import ceil, floor, isclose
from typing import Any, Callable, Iterable, Type, TypeVar, Union

from . import comparisons


T = TypeVar('T')


class BaseProp:
    """
    Base class for all properties.
    """
    types: Iterable[Type] = ()
    rules: Iterable[Callable] = ()

    def __init__(
            self,
            *,
            required: bool = True,
            default: Any = None,
    ):
        """
        Configure property.
        """
        self.required = required
        self.default = default

    @classmethod
    def validate_type(cls, value: Any):
        """
        Check if the value matches the prop type.

        :raise: TypeError
        :param value: value to check against `types`
        """
        if not any(isinstance(value, t) for t in cls.types):
            error_text = (
                'Trying to assign a value of type `{}` to a `{}` property.'
                ' Valid types are: {}.'
            ).format(
                value.__class__.__name__,
                cls.__name__,
                ', '.join(map(lambda t: t.__name__, cls.types))
            )
            raise TypeError(error_text)

    @classmethod
    def validate_rules(cls, value: Any):
        """
        Check if the value follows rules.

        :raise: ValueError
        :param value: value to check against `rules`
        """
        if not all(rule(value) for rule in cls.rules):
            raise ValueError('Value `%s` does not match the rules.' % value)

    @classmethod
    def validate(cls, value: Any):
        """
        Validate the value.

        :param value: value to assign to property
        """
        cls.validate_type(value)
        cls.validate_rules(value)

    @staticmethod
    def normalize(value: T) -> T:
        """
        Transform assigned value to the expected type.

        :param value: value to transform
        :return: transformed value
        """
        return value

    @staticmethod
    def to_cypher_value(value: T) -> str:
        """
        Transform a python value to a value suitable for cypher.

        :param value: value to transform
        :return: transformed value
        """
        return json.dumps(value, ensure_ascii=False)

    @staticmethod
    def to_python_value(value: T) -> T:
        """
        Transform a cypher value to a python analogue.

        :param value: value to transform
        :return: transformed value
        """
        return value

    def _comparison_creator(
            self,
            comparison_type: Type[comparisons.Comparison],
            value: Any,
    ) -> Callable:
        """
        Creator of the function to generate comparisons.

        :param comparison_type:
        :param value:
        :return:
        """
        def comparison(
                model_type: Union['Edge', 'Node'],
                variable: str,
        ) -> comparisons.Comparison:
            """
            Function to generate a comparison object.

            :param model_type: type  of model to compare
            :param variable: variable used in cypher statement
            :return: comparison object
            """
            prop = next(
                name for name in dir(model_type)
                if getattr(model_type, name) is self
            )

            return comparison_type(model_type, variable, prop, value)

        return comparison

    def __eq__(self, other) -> Callable[[Type, str], comparisons.Comparison]:
        """
        Used for `==` comparison.
        """
        return self._comparison_creator(comparisons.Equal, other)

    def __gt__(self, other) -> Callable:
        """
        Used for `>` comparison.
        """
        return self._comparison_creator(comparisons.Greater, other)

    def __matmul__(self, other) -> Callable:
        """
        Used for `@` comparison.
        """
        return self._comparison_creator(comparisons.In, other)


class Props:
    """
    Unique class for properties for nodes and edges.
    """
    class Boolean(BaseProp):
        """
        Boolean property.
        """
        types = (bool,)

    class Integer(BaseProp):
        """
        Integer property.
        """
        types = (int,)
        rules = (
            lambda x: x < 9223372036854775808,  # Neo4j constraint
            lambda x: x >= -9223372036854775808,  # Neo4j constraint
        )

    class Float(BaseProp):
        """
        Float property.
        """
        types = (int, float)

        @staticmethod
        def normalize(value: Union[int, float]) -> float:
            """
            Transform the value to `float`.

            :param value: value to transform
            :return: transformed value
            """
            return float(value)

    class String(BaseProp):
        """
        String property.
        """
        types = (str,)

    class Date(BaseProp):
        """
        Date property. Does not have native support for date objects in Neo4j,
        so converted to integer when saved to DB. In Python datetime.date is
        used.
        """
        types = (date, datetime)

        @staticmethod
        def normalize(value: Union[date, datetime]) -> date:
            """
            Transform the value to `date`.

            :param value: value to transform
            :return: transformed value
            """
            if isinstance(value, datetime):
                return value.date()

            return value

        @staticmethod
        def to_cypher_value(value: date) -> str:
            """
            Transform a `date` value to a stringified ordinal value.

            :param value: value to transform
            :return: transformed value
            """
            return str(value.toordinal())

        @staticmethod
        def to_python_value(value: int) -> date:
            """
            Transform an ordinal `int` to a `date` value.

            :param value: value to transform
            :return: transformed value
            """
            return date.fromordinal(value)

    class DateTime(BaseProp):
        """
        Datetime property. Does not have native support for datetime objects in
        Neo4j, so converted to timestamp when saved to DB. In Python
        datetime.date is used.
        """
        types = (date, datetime)

        @staticmethod
        def normalize(value: Union[date, datetime]) -> datetime:
            """
            Transform the value to `datetime`.

            :param value: value to transform
            :return: transformed value
            """
            if isinstance(value, date) and not isinstance(value, datetime):
                return datetime(*value.timetuple()[:3])

            return value

        @staticmethod
        def to_cypher_value(value: datetime) -> str:
            """
            Transform a `datetime` value to a stringified microtimestamp.

            :param value: value to transform
            :return: transformed value
            """
            result = value.timestamp() * 1_000_000

            low: int = floor(result)
            return str(low) if isclose(low, result) else str(ceil(result))

        @staticmethod
        def to_python_value(value: int) -> datetime:
            """
            Transform a microtimestamp `int` to a `datetime`.

            :param value: value to transform
            :return: transformed value
            """
            return datetime.fromtimestamp(value / 1_000_000)
