# Atomic

```python
with Atomic() as transaction:
    user, = FirstDB().create(user).result(transaction=transaction)[0]
    SecondDB().create(account).result(None, transaction=transaction)
```
```cypher
// Query to the first database.
CREATE (a:User) RETURN a
// Query to the second database.
CREATE (a:Account)
```
