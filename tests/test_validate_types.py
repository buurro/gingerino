import ipaddress
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from gingerino import Gingerino


@dataclass
class DataClassField:
    string_field: str
    int_field: int


class Validator(Gingerino):
    string_field: str

    int_field: int
    float_field: float
    decimal_field: Decimal

    literal_field: Literal["this", "that"]
    literal_int_field: Literal[12, 24]

    dataclass_field: DataClassField

    ip_address_field: ipaddress.IPv4Address


def test_string():
    assert Validator("{{ string_field }}").validate("Hi!")


def test_numeric():
    validator = Validator("{{ int_field }}")
    assert validator.validate("42")
    assert not validator.validate("42.5")
    assert not validator.validate("forty-two")

    validator = Validator("{{ float_field }}")
    assert validator.validate("42")
    assert validator.validate("42.5")
    assert not validator.validate("forty-two")

    validator = Validator("{{ decimal_field }}")
    assert validator.validate("42")
    assert validator.validate("42.5")
    assert not validator.validate("forty-two")


def test_literal():
    validator = Validator("{{ literal_field }}")
    assert validator.validate("this")
    assert validator.validate("that")
    assert not validator.validate("other")


def test_literal_int():
    validator = Validator("{{ literal_int_field }}")
    assert validator.validate("12")
    assert validator.validate("24")
    assert not validator.validate("42")
    assert not validator.validate("forty-two")


def test_ip_address():
    validator = Validator("{{ ip_address_field }}")
    assert validator.validate("192.168.1.1")
    assert not validator.validate("192.168.888.888")


def test_subclass():
    validator = Validator("{{ dataclass_field.string_field }}")
    assert validator.validate("some text")

    validator = Validator("{{ dataclass_field.int_field }}")
    assert validator.validate("42")
    assert not validator.validate("42.5")
