# CRUD

## Simple example
```python
class User(Node):
    class Meta(Node.Meta):
        primary_key = 'email'

    email = Props.Email(unique=True)
    password = Props.String()
```

### Create
```python
user = User(email='admin@localhost', password='some_password')
user, = Query()\
    .create(user)\
    .result()\
    [0]
```
```cypher
CREATE (_a:User {email: "admin@localhost", password: "some_password"})
RETURN _a
```

### Retrieve
```python
user, = Query()\
    .match(User)\
    .where(User.email == 'admin@localhost')\
    .result()\
    [0]
```
```cypher
MATCH (_a:User)
WHERE _a.email = 'admin@localhost'
RETURN _a
```

### Update
```python
# `user` should be fetched from the database
user.password = 'some_new_password'
user, = Query()\
    .update(user)\
    .result()\
    [0]
```
```cypher
MATCH (_a:User)
WHERE _a.email = "admin@localhost"
SET _a.password = 'some_new_password'
RETURN _a
```

### Delete
```python
Query()\
    .match(User)\
    .where(User.email == 'admin@localhost')\
    .delete()
```
```cypher
MATCH (_a:User)
WHERE _a.email = "admin@localhost"
DETACH DELETE _a
```

## Complex example
```python
class User(Node):
    class Meta(Node.Meta):
        primary_key = 'email'

    email = Props.Email(unique=True)


class Knows(Edge):
    class Meta(Edge.Meta):
        primary_key = 'uid'

    uid = Props.String(unique=True, default=lambda: uuid.uuid4().hex)
    since = Props.Date()
```

### Create
```python
john = User(email='john@localhost')
dow = User(email='dow@localhost')
knows = Knows(john, dow, since=datetime.date(1999, 10, 5))

john, knows, dow = Query()\
    .create(john, knows, dow)\
    .result()\
    [0]
# If you don't need `john` to be returned, but it already exists - don't mention
#  him in the `create` statement. If `dow` not mentioned - it will still be
#  created, but not returned.
knows, = Query()\
    .create(knows)\
    .result()\
    [0]
```
```cypher
CREATE (_a:User {email: 'john@localhost'}),
       (_c:User {email: 'dow@localhost'}),
       (_a)-[_b:Knows {since: 730032}]->(_c)
RETURN _a, _b, _c
// and if `john` existed before and was not mentioned in `create`
MATCH (_a:User)
WHERE _a.email = 'john@localhost'
CREATE (_c:User {email: 'dow@localhost'}),
       (_a)-[_b:Knows {since: 730032}]->(_c)
RETURN _b
```

### Retrieve
```python
knows, dow = Query()\
    .match(User, 'john')\
    .where(User.email == 'john@localhost')\
    .connected_through(Knows, 'knows')\
    .where(Knows.since >= date(1990, 1, 1))\
    .to(User, 'dow')\
    .where(
        User.email.startswith('dow'),
        Value('john.email') != Value('dow.email')
    )\
    .result('knows', 'dow')\
    [0]
```
```cypher
MATCH (john:User)-[knows:Knows]->(dow:User)
WHERE john.email = 'john@localhost'
  AND knows.since >= 730032
  AND dow.email STARTS WITH 'dow'
  AND john.email <> dow.email
RETURN knows
```

### Update
```python
dow.email = 'another@localhost'
knows.since = datetime.date(2000, 1, 1)

dow, = Query()\
    .update(dow, 'dow')\
    .update(knows)\
    .result('dow')\
    [0]
```

### Delete
```python
# This will delete `john` and `dow`. `knows` will be deleted too because an edge
#  cannot exist without any of its nodes.
Query().delete(john, dow)

# This will delete all the users, whom John knows. All the edges of those users
#  will be deleted too.
Query()\
    .match(john)\
    .connected_through(Knows)\
    .by(User, 'friend')\
    .delete('friend')
```
```cypher
MATCH (_a:User), (_b:User)
WHERE _a.email = 'john@localhost'
  AND _b.email = 'dow@localhost'
DETACH DELETE _a, _b

// second example
MATCH (_a:User)<-[_b:Knows]-(friend:User)
WHERE _a.email = 'john@localhost'
DETACH DELETE friend
```
