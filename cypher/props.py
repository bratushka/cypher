from typing import Any, Callable, Iterable, Type


class BaseProp:
    types: Iterable[Type] = ()
    rules: Iterable[Callable] = ()

    def __init__(
        self,
        *,
        required: bool=False,
    ):
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


class Props:
    """
    Unique class for properties for nodes and edges.
    """
    class Boolean(BaseProp):
        types = (bool,)

    class Integer(BaseProp):
        types = (int,)
        rules = (
            lambda x: x < 1 << 63,
            lambda x: x >= -1 << 63,
        )

    class Float(BaseProp):
        types = (int, float)

    class String(BaseProp):
        types = (str,)
