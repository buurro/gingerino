import pytest
from dataclasses import dataclass
from gingerino import Gingerino
from gingerino.main import TemplateError


def test_invalid_property():
    @dataclass
    class Drink:
        name: str

    with pytest.raises(TemplateError) as error:
        Gingerino(Drink, "{{ name }} {{ stuff }}")

    assert str(error.value) == "'stuff' is not valid"
