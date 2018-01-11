# CRUD

## Simple example
```python
class User(Node):
    email = Props.Email(unique=True)
    password = Props.String()
```

### Create
```python
user = User(email='admin@localhost', password='some_password')
user, = (DB()
    .create(user)
    .result()
    [0]
)
```

### Retrieve
```python
user, = (DB()
    .match(User)
    .where(User.email == 'admin@localhost')
    .result()
    [0]
)
```

### Update
```python
user.password = 'some_new_password'
user, = (DB()
    .update(user)
    .result()
    [0]
)
```

### Delete
```python
(DB()
    .delete(user)
    .result()
)
#or
(DB()
    .match(User)
    .where(User.email == 'admin@localhost')
    .delete()
    .result()
)
```

## Complex example
```python
class User(Node):
    email = Props.Email()


class Knows(Edge):
    since = Props.Date()
```

### Create
```python
john = User(email='john@localhost')
dow = User(email='dow@localhost')
knows = Knows(john, dow, since=datetime.date(1999, 10, 5))

john, knows, dow = (DB()
    .create(john, knows, dow)
    .result()
    [0]
)
# If you don't need `john` - don't mention him in the `create` statement.
# He will still be created in the database because `knows` instance depends on
#  it. If `john` was fetched from database (so we are sure he exists) - he will
#  not be created again.
knows, dow = (DB()
    .create(knows)
    .create(dow)
    .result()
    [0]
)
```

### Retrieve
```python
knows, dow = (DB()
    .match(User, 'john')
    .where(User.email == 'john@localhost')
    .connected_through(Knows, 'knows')
    .where(Knows.since >= datetime.date(1990, 1, 1))
    .to(User, 'dow')
    .where(User.email.startswith('dow'))
    .result('knows', 'dow')
    [0]
)
```

### Update
```python
dow.email = 'another@localhost'
knows.since = datetime.date(2000, 1, 1)

dow, = (DB()
    .update(dow, 'dow')
    .update(knows, 'knows')
    .result('dow')
    [0]
)
```

### Delete
```python
# This will delete `john` and `dow`. `knows` will be deleted too because an edge
#  cannot exist without any of its nodes.
(DB()
    .delete(john, dow)
    .result()
)

# This will delete all the users, whom John knows. All the edges of those users
#  will be deleted too.
(DB()
    .match(User)
    .where(User.email == 'john@localhost')
    .connected_through(Knows)
    .to(User, 'a')
    .delete('a')
    .result()
)
```
