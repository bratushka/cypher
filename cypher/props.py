from datetime import date, datetime
from typing import Any, Callable, Iterable, Type, TypeVar


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
        required: bool=False,
    ):
        """
        Configure property.

        :param required: if None value is acceptable.
        """
        self.required = required

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

    @classmethod
    def to_cypher_value(cls, value: T) -> T:
        """
        Transform a python value to a value suitable for cypher.

        :param value: value to transform
        :return: transformed value
        """
        return value

    @classmethod
    def to_python_value(cls, value: T) -> T:
        """
        Transform a cypher value to a python analogue.

        :param value: value to transform
        :return: transformed value
        """
        return value


class Props:
    """
    Unique class for properties for nodes and edges.
    """
    class Boolean(BaseProp):
        types = (bool,)

    class Integer(BaseProp):
        types = (int,)
        rules = (
            lambda x: x < 9223372036854775808,  # Neo4j constraint
            lambda x: x >= -9223372036854775808,  # Neo4j constraint
        )

    class Float(BaseProp):
        types = (int, float)

    class String(BaseProp):
        types = (str,)

    class Date(BaseProp):
        types = (date, datetime)

    class DateTime(BaseProp):
        types = (date, datetime)
