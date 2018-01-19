# Config

```python
from cypher import Config


databases = {
    'default': {
        'url': 'bolt://localhost:7687/',
        'username': 'neo4j',
        'password': 'cypher',
    },
    'special': {
        'url': 'bolt://some.url:12345/database/',
        'username': 'admin',
        'password': 'super-secret-password',
    },
}
Config.set_databases(databases)
Config.set_testing(True)
```
