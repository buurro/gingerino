# Gingerino

## Usage

```python
from typing import Literal

from gingerino import Gingerino

template: str = "{{ name }} is {{ age }} {{ unit }} old"


class Validator(Gingerino):
    name: str
    age: int
    unit: Literal["years", "months"]


validator = Validator(template)


validator.validate("Marco is 24 years old")
# True

validator.validate("This will fail")
# False

validator.validate("Marco is 24 meters old")
# False
```
