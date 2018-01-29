import json
from typing import Any


class Comparison:
    """
    Common logic for all comparisons.
    """
    def stringify(self):
        raise NotImplementedError


class Equality(Comparison):
    def __init__(self, variable: str, prop: str, value: Any):
        self.var = variable
        self.prop = prop
        self.value = json.dumps(value)

    def stringify(self):
        return '{}.{} = {}'.format(self.var, self.prop, self.value)
