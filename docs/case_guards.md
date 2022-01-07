# Case guards

```python
from apm import *

value = (7, 3)

result = case(value) \
    .of(('x' @ _, 'y' @ _), guarded(
        lambda x, y: x > y, "x is bigger than y",
        lambda x, y: x == y, "x equals y"
    )) \
    .otherwise("not an interesting case")
```
