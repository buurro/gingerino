from dataclasses import dataclass
from typing import Literal

from gingerino import parserino


@dataclass
class UserData:
    name: str
    age: int
    unit: Literal["years", "months"]


def test_success():
    template = "{{ name }} is {{ age }} {{ unit }} old"
    sample_string = "Marco is 24 years old"

    user_data = parserino(UserData, template, sample_string)

    assert user_data.name == "Marco"
    assert user_data.age == 24
    assert user_data.unit == "years"
