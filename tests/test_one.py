from typing import Literal

from gingerino import Gingerino

template: str = "{{ name }} is {{ age }} {{ unit }} old"


class Validator(Gingerino):
    name: str
    age: int
    unit: Literal["years", "months"]


validator = Validator(template)


def test_success():
    assert validator.validate("Marco is 24 years old")


def test_fail_template():
    assert not validator.validate("This will fail")


def test_fail_type():
    assert not validator.validate("Marco is twenty-four years old")
    assert not validator.validate("Marco is 24 meters old")
