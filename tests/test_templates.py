import pytest
from gingerino import Gingerino
from gingerino.main import TemplateError


def test_invalid_property():
    class Drink(Gingerino):
        name: str

    with pytest.raises(TemplateError) as error:
        Drink("{{ name }} {{ stuff }}")

    assert str(error.value) == "'stuff' is not valid"
