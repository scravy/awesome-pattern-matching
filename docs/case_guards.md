<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Case guards](#case-guards)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

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
