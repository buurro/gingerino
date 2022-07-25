from dataclasses import dataclass
from ipaddress import IPv4Address
from typing import Literal

from gingerino import Gingerino


class UserData(Gingerino):
    name: str
    age: int
    unit: Literal["years", "months"]


template: str = "{{ name }} is {{ age }} {{ unit }} old"
user_data = UserData(template)


def test_success():
    assert user_data.parse("Marco is 24 years old")
    assert user_data.name == "Marco"
    assert user_data.age == 24
    assert user_data.unit == "years"


def test_fail():
    assert not user_data.parse("Something")


def test_subclass():
    @dataclass
    class Connection:
        ip: IPv4Address
        port: int

    class ConnectedUser(Gingerino):
        name: str
        connection: Connection

    template = (
        "User '{{ name }}' connected from {{ connection.ip }}:{{ connection.port }}"
    )
    user = ConnectedUser(template)

    assert user.parse("User 'marco' connected from 192.168.1.2:12987")

    assert user.name == "marco"
    assert user.connection.ip == IPv4Address("192.168.1.2")
    assert user.connection.port == 12987
