"""
Conditions for queries.
"""
import functools
from typing import Any, Callable, Mapping, Type


class Value:
    """
    Represent any type of value.
    """
    def __init__(
            self,
            expr: str = None,
            *,
            prop: 'BaseProp' = None,
            wrappers: Callable[[str], str] = None,
    ):
        self.expr = expr
        self.prop = prop
        self.wrappers = wrappers or []

    def _cypherify_other(self, other: Any, var: str) -> str:
        """
        Transform python object into string.

        :param other: value to compare with
        :return: cypherified value
        """
        if isinstance(other, Value):
            return '%s.%s' % (other.var or var, other.prop)

        other = self.prop.normalize(other)
        self.prop.validate(other)

        return self.prop.to_cypher_value(other)

    def _comparison_builder(
            self,
            other: Any,
            operator: str,
    ) -> Callable[[Mapping[str, 'ModelDetails'], str], str]:
        """
        Build the function that given the variable will return a cypher
        condition.

        :param other: value to compare with
        :param operator: cypher operator to apply
        :return:
        """
        def comparison(
                details: Mapping[str, 'ModelDetails'],
                current_var: str,
        ) -> str:
            """
            Comparison creator.
            """
            if self.expr:
                var, prop_name = self.expr.split('.')
                current_details = details[var]
                self.prop = getattr(current_details.type, prop_name)
            else:
                current_details = details[current_var]
                prop_name = next(
                    name
                    for name in dir(current_details.type)
                    if getattr(current_details.type, name) is self.prop
                )

            return ' '.join((
                functools.reduce(
                    lambda value, wrapper: wrapper(value),
                    self.wrappers,
                    '.'.join((current_var, prop_name)),
                ),
                operator,
                self._cypherify_other(other, current_details.var),
            ))

        return comparison

    # def _convert_value(self, value_type: Type['Value']) -> 'Value':
    #     # prop = '.'.join((self.var, self.prop)) if self.var else self.prop
    #     result = value_type(
    #         expr=self.expr,
    #         prop=self.prop,
    #         wrappers=self.wrappers,
    #     )

    # def to_bool(self) -> 'BooleanValue':
    #     """
    #     Convert Value to BooleanValue.
    #     """
    #     def wrapper(value: str) -> str:
    #         """
    #         Wrap the value in `toBoolean` function.
    #         """
    #         return 'toBoolean(%s)' % value
    #
    #     converted: BooleanValue = self._convert_value(BooleanValue)
    #     converted.wrappers.append(wrapper)
    #
    #     return converted

    def __eq__(self, other: Any) -> Callable[[str], str]:
        return self._comparison_builder(other, '=')

    def __gt__(self, other: Any) -> Callable[[str], str]:
        return self._comparison_builder(other, '>')


# class BooleanValue(Value):
#     """
#     Represent boolean value.
#     """
#     prop_type = Props.Boolean
#
#
# class NumericValue(Value):
#     """
#     Represent numeric value.
#     """
#
#
class StringValue(Value):
    """
    Represent string value.
    """
    def lower(self) -> 'StringValue':
        """
        Add `toLower` wrapper.
        """
        def wrapper(value: str) -> str:
            """
            Wrap a string value with `toLower`.
            """
            return 'toLower(%s)' % value

        self.wrappers.append(wrapper)

        return self
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
