from dataclasses import dataclass
from decimal import Decimal

import pytest

from gingerino import Gingerino
from gingerino.main import TemplateError


def test_valid_template():
    @dataclass
    class Drink:
        name: str

    Gingerino(Drink, "{{ name }}")


def test_invalid_property():
    @dataclass
    class Drink:
        name: str

    with pytest.raises(TemplateError) as error:
        Gingerino(Drink, "{{ name }} {{ stuff }}")

    assert str(error.value) == "'stuff' is not valid"


def test_missing_property():
    @dataclass
    class Drink:
        name: str
        price: Decimal

    with pytest.raises(TemplateError) as error:
        Gingerino(Drink, "{{ name }}")

    assert str(error.value) == "required field 'price' is missing"
