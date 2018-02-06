"""
Conditions for queries.
"""
import functools
from typing import Any, Callable, Type

from .props import BaseProp, Props


class Value:
    """
    Represent any type of value.
    """
    prop_type = BaseProp

    def __init__(
            self,
            prop: str = None,
            *,
            wrappers: Callable[[str], str] = None,
    ):
        if '.' in prop:
            self.var, self.prop = prop.split('.')
        else:
            self.prop = prop
            self.var = None

        self.wrappers = wrappers or []

    @classmethod
    def _cypherify_other(cls, other: Any) -> str:
        """
        Transform python object into string.

        :param other: value to compare with
        :return: cypherified value
        """
        if isinstance(other, Value):
            return '%s.%s' % (other.var, other.prop)

        other = cls.prop_type.normalize(other)
        cls.prop_type.validate(other)

        return cls.prop_type.to_cypher_value(other)

    def _comparison_builder(
            self,
            other: Any,
            operator: str,
    ) -> Callable[[Any, str], str]:
        """
        Build the function that given the variable will return a cypher
        condition.

        :param other: value to compare with
        :param operator: cypher operator to apply
        :return:
        """
        def comparison(var: str) -> str:
            """
            Comparison creator.
            """
            return ' '.join((
                functools.reduce(
                    lambda value, wrapper: wrapper(value),
                    self.wrappers,
                    '.'.join((self.var or var, self.prop)),
                ),
                operator,
                self._cypherify_other(other),
            ))

        return comparison

    def _convert_value(self, value_type: Type['Value']) -> 'Value':
        prop = '.'.join((self.var, self.prop)) if self.var else self.prop

        return value_type(prop, wrappers=self.wrappers)

    def to_bool(self) -> 'BooleanValue':
        """
        Convert Value to BooleanValue.
        """
        def wrapper(value: str) -> str:
            """
            Wrap the value in `toBoolean` function.
            """
            return 'toBoolean(%s)' % value

        converted: BooleanValue = self._convert_value(BooleanValue)
        converted.wrappers.append(wrapper)

        return converted

    def __eq__(self, other: Any) -> Callable[[str], str]:
        return self._comparison_builder(other, '=')

    def __gt__(self, other: Any) -> Callable[[str], str]:
        return self._comparison_builder(other, '>')


class BooleanValue(Value):
    """
    Represent boolean value.
    """
    prop_type = Props.Boolean
#
#
# class NumericValue(Value):
#     """
#     Represent numeric value.
#     """
#
#
# class StringValue(Value):
#     """
#     Represent string value.
#     """
#
#
# class DateValue(Value):
#     """
#     Represent date value.
#     """
#
#
# class DateTimeValue(Value):
#     """
#     Represent datetime value.
#     """
