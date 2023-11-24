# Gingerino

[![PyPI Version](https://img.shields.io/pypi/v/gingerino)](https://pypi.org/project/gingerino/)

This is a proof of concept

## Installation

```bash
pip install gingerino
```

## Usage

```python
from dataclasses import dataclass
from typing import Literal

from gingerino import parserino


@dataclass
class UserInfo:
    name: str
    age: int
    unit: Literal["years", "months"]


template = "{{ name }} is {{ age }} {{ unit }} old"
user = parserino(UserInfo, template, "Marco is 24 years old")

print(user.name, user.age)
# Marco 24
```
