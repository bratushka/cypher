# Query API

## Chains

### Matching chain

Starts with `Query().match()` or right after another Matching chain. Finishes
 before any of:
1. `.match()`
1. `.create()`
1. `.update()`
1. `.result()`
1. `.delete()`

Can contain any number of`.where()` methods anywhere except the first position.

#### Examples:

Simple:

```python
Query().match(User).result()
```

```cypher
MATCH (_a:User)
RETURN _a
```

Complex:

```python
Query()\
    .match(User, 'a')\
    .where(User.age > 21)\
    .connected_through(Knows, conn=(None, 2))\
    .where(Knows.starting_from < datetime.date(1, 2, 3))\
    .to(User, 'b')\
    .where(Value('b.age') > Value('a.age'))\
    .where(User.age < 99)\
    .connected_through(Hired, 'hired')\
    .by(Company)\
    .where(Company.name == 'ACME')\
    .match(Job, 'c')\
    .result('b', 'c')
```

```cypher
MATCH _p1 = (a:User)-[_a:Knows *..2]->(b:User)
WITH *, relationships(_p1) as _a
WHERE a.age > 21
  AND all(el in _a WHERE el.starting_from < 34)
  AND b.age > a.age
  AND b.age < 99
MATCH _p2 = (b)<-[hired:Hired]-(_b:Company)
WHERE _b.name = 'ACME'
MATCH (c:Job)
RETURN b, c
```

---

### Creation and Update chains

Can start from `Query().create()` or `Query().update()` or right after a
 Matching chain.

#### Examples

Simple:

```python
user = User(name='Kate')
Query().create(user).result(None)
```

```cypher
CREATE (:User {name: "Kate"})
```

Complex:

```python
# `john` is fetched from database. He joined the ACME company today, so
#  everybody in his new working place knows him now. He knows himself too, but
#  we will not store this information.
friends = Query()\
    .match(User)\
    .where(
        User.email != john.email,
        User.company == 'ACME',
    )\
    .result()

today = datetime.date.today()
Query()\
    .create(*map(
        lambda friend: Knows(friend, john, starting_from=today),
        friends,
    ))\
    .result(None)
```

```cypher
// First query.
MATCH (_a:User)
WHERE _a.email <> "john@localhost"
  AND _a.company = "ACME"
RETURN _a

// Second query.
MATCH (_a:User)
WHERE _a.email = "friend_1@localhost"
MATCH (_b:User)
WHERE _b.email = "john@localhost"
MATCH (_c:User)
WHERE _c.email = "friend_2@localhost"
MATCH (_d:User)
WHERE _d.email = "friend_3@localhost"
// and so on till we find all the friends
CREATE (_a)-[_wa:Knows {starting_from: 123123}]->(_b),
       (_c)-[_wa:Knows {starting_from: 123123}]->(_b),
       (_d)-[_wa:Knows {starting_from: 123123}]->(_b)
// and so on till we create all the edges
```
