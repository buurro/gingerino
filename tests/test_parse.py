from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address
from typing import Literal

import pytest

from gingerino import Gingerino, parserino
from gingerino.main import ValidationError


@dataclass
class UserData:
    name: str
    age: int
    unit: Literal["years", "months"]


template: str = "{{ name }} is {{ age }} {{ unit }} old"


def test_success():
    user_data = parserino(UserData, template, "Marco is 24 years old")
    assert user_data.name == "Marco"
    assert user_data.age == 24
    assert user_data.unit == "years"


def test_fail():
    with pytest.raises(ValidationError):
        parserino(UserData, template, "Something")


def test_subclass():
    @dataclass
    class Connection:
        ip: IPv4Address
        port: int

    @dataclass
    class ConnectedUser:
        name: str
        connection: Connection

    template = (
        "User '{{ name }}' connected from {{ connection.ip }}:{{ connection.port }}"
    )
    input_string = "User 'marco' connected from 192.168.1.2:12987"

    user = parserino(ConnectedUser, template, input_string)

    assert user.name == "marco"
    assert user.connection.ip == IPv4Address("192.168.1.2")
    assert user.connection.port == 12987


def test_empty_string():
    @dataclass
    class Data:
        name: str

    assert parserino(Data, "{{ name }}", "").name == ""


def test_union():
    @dataclass
    class Data:
        ip: IPv4Address | IPv6Address

    parser = Gingerino(Data, "{{ ip }}")

    assert parser.parse("127.0.0.1").ip == IPv4Address("127.0.0.1")
    assert parser.parse("::1").ip == IPv6Address("::1")

    with pytest.raises(ValidationError):
        parser.parse("888.888.888.888")
