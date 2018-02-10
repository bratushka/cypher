"""
Properties for models.
"""
from typing import Any, Callable, Iterable, Type, TypeVar

from . import values


T = TypeVar('T')


class BaseProp:
    """
    Base class for all properties.
    """
    types: Iterable[Type] = (object,)
    rules: Iterable[Callable] = ()
    value_type = values.Value

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
        self._default = default if callable(default) else lambda: default

    @property
    def default(self):
        """
        :return: computed default value
        """
        return self._default()

    # def __eq__(self, other):
    #     return self.value_type(prop=self) == other
    #
    # def __gt__(self, other):
    #     return self.value_type(prop=self) > other


class Props:
    """
    Unique class for properties for nodes and edges.
    """
    class Boolean(BaseProp):
        """
        Boolean property.
        """
        value_type = values.Boolean

    class Integer(BaseProp):
        """
        Integer property.
        """
        value_type = values.Integer

    class Float(BaseProp):
        """
        Float property.
        """
        value_type = values.Float

    class String(BaseProp):
        """
        String property.
        """
        value_type = values.String

        # def lower(self) -> StringValue:
        #     """
        #     `toLower` wrapper for cypher query.
        #     """
        #     return self.value_type(prop=self).lower()

    class Date(BaseProp):
        """
        Date property.
        """
        value_type = values.Date

    class DateTime(BaseProp):
        """
        Datetime property.
        """
        value_type = values.DateTime
