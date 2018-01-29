from typing import Any, Type

from .models import Model


class Comparison:
    """
    Common logic for all comparisons.
    """
    sign = ''

    def __init__(self, cls: Type[Model], variable: str, prop: str, value: Any):
        self.var = variable
        self.prop = prop
        self.value = getattr(cls, prop).to_cypher_value(value)

    def stringify(self):
        return '{}.{} {} {}'.format(self.var, self.prop, self.sign, self.value)


class Equal(Comparison):
    sign = '='


class Greater(Comparison):
    sign = '>'
