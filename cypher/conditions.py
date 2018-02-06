"""
Conditions for queries.
"""
from typing import Any

from .props import BaseProp


class Value:
    """
    Represent any type of value.
    """
    prop_type = BaseProp

    def __init__(
            self,
            var: str = None,
            prop: str = None,
    ):
        self.var = var
        self.prop = prop

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

    def __eq__(self, other: Any) -> str:
        """
        Check the value for equality.

        :param other: value to compare with
        :return: stringified condition
        """
        other = self._cypherify_other(other)

        return '%s.%s = %s' % (self.var, self.prop, other)


# class BooleanValue(Value):
#     """
#     Represent boolean value.
#     """
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
