import re
from typing import get_type_hints


class Gingerino:
    _template: str

    def __init__(self, template: str):
        self._template = template

    def validate(self, text: str) -> bool:
        pattern = re.compile(r"\{\{\s*(\w+)\s+\}\}")
        variables = pattern.findall(self._template)

        pattern = re.compile(r"\{\{\s*\w+\s+\}\}")
        non_matched = pattern.split(self._template)

        pattern_str = r"(.*)".join([re.escape(nm) for nm in non_matched])
        pattern = re.compile(pattern_str)
        result = pattern.findall(text)
        if not result:
            return False
        values = result[0]

        attribute_annotations = get_type_hints(self)

        print(variables, values)

        for variable, value in zip(variables, values):
            if variable not in attribute_annotations:
                raise AttributeError(f"{variable} is not a valid variable")

            try:
                _ = attribute_annotations[variable](value)
            except Exception:
                return False

        return True
