```cypher
MATCH (a:User)-[b:Parent]->(c:User)
WHERE a.dob > 123123
    AND b.dob < 9123123
    AND a.dob = b.dob
RETURN a, b, c
```
```python
(DB()
    .match(User, 'a')
    .where(User.dob > 123123)
    .connected(Parent, 'b')
    .where(Parent.q == 2)
    .to(User, 'c')
    .where(User.dob < 4)
    .where(Value('a.dob') == Value('b.dob'))
    .result()
)
```
---
```cypher
MATCH (a:Restaurant),(b:Category)
WHERE a["rating_" + b.name] > 6
RETURN DISTINCT a.name
```
```python
(DB()
    .match(User, 'a')
    .match(User, 'b')
    .where(Value('a["rating_" + b.name]') > 6)
    .result('a.name', distinct=True)
)
```
---
```cypher
MATCH (a), (b)
WHERE id(a) = 20
    AND id(b) = 25
CREATE (a)-[rel:Parent]->(b)
RETURN rel
```
```python
# Considering node_a and node_b are the instances of Node populated from DB
(DB()
    .create(Parent(node_a, node_b), 'rel')
    .result()
)
```
```python
# If we know the IDs of the nodes, but didn't fetch them before from DB
(DB()
    .match(Node, 'a')  # base Node class to avoid adding `label` to the query
    .where(Id(Node) == 20)
    .match(Node, 'b')
    .where(Id(Node) == 25)
    .create(Parent('a', 'b'), 'rel')
    .result('rel')
)
```
