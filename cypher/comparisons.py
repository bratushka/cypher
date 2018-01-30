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
        self.var = variable
        self.prop = prop
        self.value = getattr(cls, prop).to_cypher_value(value)

    def stringify(self):
        return '{}.{} {} {}'.format(
            self.var,
            self.prop,
            self.operator,
            self.value
        )


class Equal(Comparison):
    operator = '='


class Greater(Comparison):
    operator = '>'


class In(Comparison):
    operator = 'IN'
