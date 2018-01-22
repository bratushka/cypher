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
user, = (Query()
    .create(user)
    .result()
    [0]
)
```
```cypher
CREATE
    (a:User { email: 'admin@localhost', password: 'some_password' })
RETURN a
```

### Retrieve
```python
user, = (Query()
    .match(User, User.email == 'admin@localhost')
    .result()
    [0]
)
```
```cypher
MATCH
    (a:User { email: 'admin@localhost' })
RETURN a
```

### Update
```python
# `user` should be fetched from the database, so having an internal ID
user.password = 'some_new_password'
user, = (Query()
    .update(user)
    .result()
    [0]
)
```
```cypher
MATCH
    (a)
WHERE
    id(a) = 12345
SET
    a.password = 'some_new_password'
RETURN a
```

### Delete
```python
(Query()
    .delete(user)
    .result()
)
# or
(Query()
    .match(User, User.email == 'admin@localhost')
    .where(Value('email') == 'admin@localhost')
    .delete()
    .result()
)
```
```cypher
MATCH
    (a)
WHERE
    id(a) = 12345
DETACH DELETE a
// or
MATCH
    (a:User { email: 'admin@localhost' })
DETACH DELETE a
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

john, knows, dow = (Query()
    .create(john, knows, dow)
    .result()
    [0]
)
# If you don't need `john` to be returned, but it already exists - don't mention
#  him in the `create` statement.
knows, dow = (Query()
    .create(knows, dow)
    .result()
    [0]
)
```
```cypher
CREATE
    (a:User { email: 'john@localhost' }),
    (b:User { email: 'dow@localhost' }),
    (a)-[c:Knows { since: 730032 }]->(b)  // date(1999, 10, 5).toordinal()
RETURN a, c, b
// and if `john` existed before and was not mentioned in `create`
MATCH
    (a)
WHERE
    id(a) = 12345
CREATE
    (b:User { email: 'dow@localhost' }),
    (a)-[c:Knows { since: 730032 }]->(b)
RETURN a, c, b
```

### Retrieve
```python
knows, dow = (Query()
    .match((User, 'john'), User.email == 'john@localhost')
    .connected_through((Knows, 'knows'), Knows.since >= date(1990, 1, 1))
    .to((User, 'dow'), User.email.startswith('dow'))
    .where(Value('john.email') != Value('dow.email'))
    .result('knows', 'dow')
    [0]
)
```
```cypher
MATCH
    (john:User { email: 'john@localhost' })-[knows:Knows]->(dow:User)
WHERE
    knows.since >= 730032
AND dow.email STARTS WITH 'dow'
AND john.email <> dow.email
RETURN knows, dow
```

### Update
```python
dow.email = 'another@localhost'
knows.since = datetime.date(2000, 1, 1)

dow, = (Query()
    .update((dow, 'dow'), knows)
    .result('dow')
    [0]
)
```

### Delete
```python
# This will delete `john` and `dow`. `knows` will be deleted too because an edge
#  cannot exist without any of its nodes.
(Query()
    .delete(john, dow)
    .result()
)

# This will delete all the users, whom John knows. All the edges of those users
#  will be deleted too.
(Query()
    .match(User, User.email == 'john@localhost')
    .connected_through(Knows)
    .by((User, 'friend'))
    .delete('friend')
    .result()
)
```
```cypher
MATCH
    (a:User),
    (b:User)
WHERE
    id(a) = 12345
AND id(b) = 23456
DETACH DELETE a, b
// second example
MATCH
    (a:User { email: 'john@localhost' })<-[b:Knows]-  (friend:User)
DETACH DELETE friend
```
