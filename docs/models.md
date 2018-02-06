```python
class Person(Node):
    class Meta(Node.Meta):
        primary_key = 'email'
        unique_together = (
            ('age', 'name'),
        )
        validations = (
            (lambda obj: (obj.height + obj.age) < 30),
        )
        abstract = True
        database = 'specific'

    is_admin = Props.Boolean(
        default=True,
    )
    age = Props.Integer(
        validations=[
            lambda value: value >= 18,
        ],
    )
    height = Props.Float(
        nullable=True,
    )
    name = Props.String(
        indexed=True,
    )
    email = Props.Email(
        unique=True,
    )
    scores = Props.List(
        Props.Integer(),
    )
    keys = Props.Map(
        default=lambda: {
            'home': '$HOME$KEY$',
            'office': '$OFFICE$KEY$',
        },
    )
```
