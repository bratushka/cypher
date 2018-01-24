# Query API

## Actions

---

### `.match()`

From:
1. `Query()`

To:
1. `.create() | .update()`
1. `.result()`
1. `.delete()`
1. `.connected_through()`

---

### `.create() | .update()`

From:
1. `Query()`
1. `.match()`
1. `.to | .by()`

To:
1. `.result()`

---

### `.connected_through()`

From:
1. `.match()`
1. `.to() | .by()`

To:
1. `.to() | .by()`

---

### `.to() | .by()`

From:
1. `.connected_through()`

To:
1. `.connected_through()`
1. `.create() | .update()`
1. `.result()`
1. `.delete()`

---

## Method Chains

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
MATCH
    (a:User)
RETURN a
```

Complex:

```python
(Query()
    .match((User, 'a'))
    .where(User.age > 21)
    .connected_through(Knows)
    .where(Knows.starting_from < timedelta(days=-365))
    .to((User, 'b'))
    .where(Value('b.age') > Value('a.age'))
    .where(User.age < 99)
    .connected_through(Hired)
    .by(Company, Company.name == 'ACME')
    .match((Job, 'c'))
    .result('b', 'c')
)
```

```cypher
MATCH
    (a:User)-[random_var_1:Knows]->(b:User)<-[:Hired]-(random_var_2:Company),
    (c:Job)
WHERE
    a.age > 21
AND random_var_1.starting_from < 123123123
AND b.age > a.age
AND b.age < 99
AND random_var_2 = "ACME"
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
friends = (Query()
    .match((john, 'john'))
    .match((User, 'colleague'), User.uid != john.uid, User.company == 'ACME')
    .create(Knows('colleague', 'john', starting_from=date.today()))
    .result('colleague')
)
```

```cypher
MATCH (john:User), (colleague:User)
WHERE
    john.uid = "abc123abd456"
AND colleague.uid <> "abc123abd456"
AND colleague.company = "ACME"
CREATE (colleague)-[:Knows {starting_from: 123123}]->(john)
RETURN colleague
```
