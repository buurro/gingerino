import re
from typing import Literal, Pattern, get_origin, get_type_hints


class Gingerino:
    _template: str
    _variables: list[str]
    _non_matching_parts: list[str]

    _values_match_pattern: Pattern[str]

    def __init__(self, template: str):
        self._template = template

        pattern = re.compile(r"\{\{\s*(\w+)\s+\}\}")
        self._variables = pattern.findall(template)

        pattern = re.compile(r"\{\{\s*\w+\s+\}\}")
        self._non_matching_parts = pattern.split(template)

        pattern_str = r"(.*)".join([re.escape(nm) for nm in self._non_matching_parts])
        self._values_match_pattern = re.compile(pattern_str)

    def validate(self, text: str) -> bool:
        result = self._values_match_pattern.findall(text)
        if not result:
            return False
        values = result[0]

        attribute_annotations = get_type_hints(self)

        for variable, value in zip(self._variables, values):
            if variable not in attribute_annotations:
                raise AttributeError(f"{variable} is not a valid variable")

            annotation = attribute_annotations[variable]

            if get_origin(annotation) == Literal:
                if value not in annotation.__args__:
                    return False
            else:
                try:
                    _ = annotation(value)
                except Exception:
                    return False

        return True
