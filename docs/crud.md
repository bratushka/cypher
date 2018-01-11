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
user = (DB()
    .create(user)
    .result()
    [0]
)
```

### Retrieve
```python
user = (DB()
    .match(User)
    .where(User.email == 'admin@localhost')
    .result()
    [0]
)
```

### Update
```python
user.password = 'some_new_password'
user = (DB()
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
```
