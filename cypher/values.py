"""
Conditions for queries.
"""
import json
from datetime import date, datetime

from typing import Any, TypeVar, Union


T = TypeVar('T')


class Value:
    """
    Represent arbitrary type of value.
    """
    types = (object,)
    constraints = ()

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
    def validate_constraints(cls, value: Any):
        """
        Check if the value follows Neo4j constraints.

        :raise: ValueError
        :param value: value to check against `constraints`
        """
        if not all(constraint(value) for constraint in cls.constraints):
            error = 'Value `%s` does not meet the constraints.' % str(value)
            raise ValueError(error)

    @classmethod
    def validate(cls, value: Any):
        """
        Validate the value.

        :param value: value to assign to property
        """
        cls.validate_type(value)
        cls.validate_constraints(value)

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


class Boolean(Value):
    """
    Represent boolean value.
    """
    types = (object,)

    @staticmethod
    def normalize(value: T) -> bool:
        """
        Transform assigned value to bool.

        :param value: value to transform
        :return: transformed value
        """
        return bool(value)


class Integer(Value):
    """
    Represent integer value.
    """
    types = (int,)
    constraints = (
        lambda x: x < 9223372036854775808,
        lambda x: x >= -9223372036854775808,
    )


class Float(Value):
    """
    Represent float value.
    """
    types = (float, int)

    @staticmethod
    def normalize(value: Any) -> float:
        """
        Transform assigned value to float.

        :param value: value to transform
        :return: transformed value
        """
        return float(value)


class String(Value):
    """
    Represent string value.
    """
    types = (str,)


class Date(Value):
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


class DateTime(Value):
    """
    Datetime property. Does not have native support for datetime objects in
    Neo4j, so converted to timestamp when saved to DB. In Python
    datetime.datetime is used.
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
        Transform a `datetime` value to a stringified timestamp.

        :param value: value to transform
        :return: transformed value
        """
        return str(value.timestamp())

    @staticmethod
    def to_python_value(value: int) -> datetime:
        """
        Transform a timestamp `float` to a `datetime`.

        :param value: value to transform
        :return: transformed value
        """
        return datetime.fromtimestamp(value)
