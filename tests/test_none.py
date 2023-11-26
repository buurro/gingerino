from dataclasses import dataclass

from gingerino.main import Gingerino


def test_optional_string():
    @dataclass
    class Parser:
        optional_str: str | None

    parser = Gingerino(Parser, "-> {{ optional_str }} <-")

    assert parser.parse("->  <-").optional_str == ""


def test_optional_numeric():
    @dataclass
    class Parser:
        optional_int: int | None

    parser = Gingerino(Parser, "-> {{ optional_int }} <-")

    assert parser.parse("-> 42 <-").optional_int == 42
    assert parser.parse("->  <-").optional_int is None
