# Gingerino

## Usage

```python
from typing import Literal

from gingerino import Gingerino


class UserInfo(Gingerino):
    name: str
    age: int
    unit: Literal["years", "months"]


template: str = "{{ name }} is {{ age }} {{ unit }} old"
user = UserInfo(template)

user.parse("Marco is 24 years old")

print(user.name, user.age, user.unit)
# Marco 24 years
```
