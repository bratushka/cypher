"""
Logic for cypher condition statements.
"""
from typing import Any, Type


class Comparison:
    """
    Common logic for all comparisons.
    """
    operator = ''

    def __init__(
            self,
            cls: Type['Model'],
            variable: str,
            prop: str,
            value: Any,
    ):
        """
        :param cls: type of the model to compare
        :param variable: variable representing the model in cypher
        :param prop: name of the property
        :param value: value to compare the prop with
        """
        self.var = variable
        self.prop = prop
        self.value = getattr(cls, prop).to_cypher_value(value)

    def stringify(self) -> str:
        """
        :return: condition as it should be written in cypher
        """
        return '{}.{} {} {}'.format(
            self.var,
            self.prop,
            self.operator,
            self.value
        )


class Equal(Comparison):
    """
    Equality comparison.
    """
    operator = '='


class Greater(Comparison):
    """
    Strictly greater.
    """
    operator = '>'


class In(Comparison):
    """
    Insertion checker.
    """
    operator = 'IN'
