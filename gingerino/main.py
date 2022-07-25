import re
from dataclasses import dataclass
from typing import Any, Literal, Pattern, Type, get_origin, get_type_hints


class ValidationError(Exception):
    pass


@dataclass
class ValidationResult:
    valid: bool
    message: str

    def __bool__(self):
        return self.valid


class Gingerino:
    _template: str
    _variables: list[str]
    _non_matching_parts: list[str]

    _values_match_pattern: Pattern[str]

    def __init__(self, template: str):
        self._template = template

        pattern = re.compile(r"\{\{\s*([\w\.\[\]]+)\s+\}\}")
        self._variables = pattern.findall(template)

        pattern = re.compile(r"\{\{\s*[\w\.\[\]]+\s+\}\}")
        self._non_matching_parts = pattern.split(template)

        pattern_str = r"(.*)".join([re.escape(nm) for nm in self._non_matching_parts])
        pattern_str = f"^{pattern_str}$"
        self._values_match_pattern = re.compile(pattern_str)

    def validate(self, text: str) -> ValidationResult:
        try:
            pairs = self._get_variable_value_pairs(text)
        except ValidationError as e:
            return ValidationResult(False, str(e))

        for variable, value in pairs:
            if not self._check_if_value_matches_type(variable, value, self.__class__):
                return ValidationResult(
                    False, f"{value} is not a valid value for {variable}"
                )
        return ValidationResult(True, "")

    def parse(self, text: str) -> ValidationResult:
        validation_result = self.validate(text)

        if not validation_result:
            return validation_result

        pairs = self._get_variable_value_pairs(text)

        properties: dict[str, object] = {}
        for variable, value in pairs:
            casted_value = self._cast_value_to_type(variable, value, self.__class__)
            properties[variable] = casted_value

        self._populate_object(properties, self.__class__)

        return ValidationResult(True, "")

    def _get_variable_value_pairs(self, text: str) -> list[tuple[str, str]]:
        result = self._values_match_pattern.findall(text)
        if not result:
            raise ValidationError("No match found")

        values: list[str] | tuple[str]
        if isinstance(result[0], str):
            values = result
        else:
            values = result[0]

        if len(values) != len(self._variables):
            raise ValidationError("Number of variables does not match")

        return [tuple(pair) for pair in zip(self._variables, values)]

    def _check_if_value_matches_type(
        self, variable: str, value: str, target_class: Type[object]
    ) -> bool:
        annotations = get_type_hints(target_class)

        if "." in variable:
            current_class_property = variable.split(".", maxsplit=1)[0]
            if current_class_property not in annotations:
                return False
            child_class = annotations[current_class_property]
            return self._check_if_value_matches_type(
                variable.split(".")[1], value, child_class
            )

        if variable not in annotations:
            return False
        annotation = annotations[variable]

        if get_origin(annotation) == Literal:
            literals = [str(literal) for literal in annotation.__args__]
            if value not in literals:
                return False
        else:
            try:
                _ = annotation(value)
            except Exception:
                return False
        return True

    def _cast_value_to_type(
        self, variable: str, value: str, target_class: Type[object]
    ) -> object:
        annotations = get_type_hints(target_class)

        if "." in variable:
            current_class_property = variable.split(".", maxsplit=1)[0]
            child_class = annotations[current_class_property]
            return self._cast_value_to_type(variable.split(".")[1], value, child_class)

        annotation = annotations[variable]
        if annotation == str:
            return value
        if get_origin(annotation) == Literal:
            literals = [str(literal) for literal in annotation.__args__]
            return annotation.__args__[literals.index(value)]
        return annotation(value)

    def _populate_object(
        self, properties: dict[str, object], target_class: Type[Any]
    ) -> object:
        is_main_object = target_class == self.__class__
        children: dict[str, dict[str, object]] = {}
        current_object_properties: dict[str, object] = {}
        for variable, value in properties.items():
            if "." in variable:
                child = variable.split(".", maxsplit=1)[0]
                if child not in children:
                    children[child] = {}
                children[child][variable.split(".")[1]] = value
            else:
                current_object_properties[variable] = value

        annotations = get_type_hints(target_class)
        if is_main_object:
            for key, value in current_object_properties.items():
                setattr(self, key, value)
            for child, child_properties in children.items():
                child_class = annotations[child]
                setattr(
                    self,
                    child,
                    self._populate_object(child_properties, child_class),
                )
            return self
        else:
            for child, child_properties in children.items():
                child_class = annotations[child]
                current_object_properties[child] = self._populate_object(
                    child_properties, child_class
                )
            return target_class(**current_object_properties)
