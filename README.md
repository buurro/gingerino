# Gingerino

[![PyPI Version](https://img.shields.io/pypi/v/gingerino)](https://pypi.org/project/gingerino/)

This is a proof of concept

## Usage

```python
from typing import Literal

from gingerino import Gingerino


class UserInfo(Gingerino):
    name: str
    age: int
    unit: Literal["years", "months"]


template = "{{ name }} is {{ age }} {{ unit }} old"
user = UserInfo(template)

user.parse("Marco is 24 years old")

print(user.name, user.age, user.unit)
# Marco 24 years
```
