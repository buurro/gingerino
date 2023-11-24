import re
from dataclasses import dataclass
from typing import (
    Any,
    Literal,
    NamedTuple,
    Pattern,
    Type,
    TypeVar,
    get_origin,
    get_type_hints,
)


class ValidationError(Exception):
    pass


class TemplateError(Exception):
    pass


@dataclass
class ValidationResult:
    valid: bool
    message: str

    def __bool__(self):
        return self.valid


class Variable(NamedTuple):
    name: str
    annotation: Any

    @property
    def re_friendly_name(self):
        return self.name.replace(".", "_")

    def __str__(self):
        return self.name


class Gingerino:
    _type: Type[Any]
    _template: str
    _variables: dict[str, Variable]
    _values_match_pattern: Pattern[str]

    def __init__(self, type: Type[Any], template: str):
        self._type = type
        self._template = template

        pattern = re.compile(r"\{\{\s*([\w\.\[\]]+)\s+\}\}")
        variable_names: list[str] = pattern.findall(template)

        self._variables = {}
        for variable_name in variable_names:
            self._variables[variable_name] = Variable(
                variable_name,
                Gingerino._get_class_property_annotation(self._type, variable_name),
            )

        pattern = re.compile(r"\{\{\s*[\w\.\[\]]+\s+\}\}")
        non_matching_parts = pattern.split(template)

        pattern_str = ""
        for i, part in enumerate(non_matching_parts):
            pattern_str += re.escape(part)
            if i < len(variable_names):
                variable = self._variables[variable_names[i]]
                pattern_str += r"(?P<{}>.*)".format(variable.re_friendly_name)
        pattern_str = f"^{pattern_str}$"
        self._values_match_pattern = re.compile(pattern_str, re.DOTALL)

    def validate(self, text: str) -> ValidationResult:
        try:
            pairs = self._get_variable_value_pairs(text)
        except ValidationError as e:
            return ValidationResult(False, str(e))

        for variable, value in pairs:
            try:
                self._cast_value_to_type(variable, value)
            except Exception:
                return ValidationResult(
                    False, f"{value} is not a valid value for {variable}"
                )
        return ValidationResult(True, "")

    def parse(self, text: str) -> Any:
        validation_result = self.validate(text)

        if not validation_result:
            raise ValidationError(validation_result.message)

        pairs = self._get_variable_value_pairs(text)

        properties: dict[str, object] = {}
        for variable, value in pairs:
            casted_value = self._cast_value_to_type(variable, value)
            properties[variable.name] = casted_value

        return self._populate_object(self._type, properties)

    def _get_variable_value_pairs(self, text: str) -> list[tuple[Variable, str]]:
        result = self._values_match_pattern.match(text)
        if not result:
            raise ValidationError("No match found")
        values = result.groupdict()

        pairs: list[tuple[Variable, str]] = []
        for variable in self._variables.values():
            value = values[variable.re_friendly_name]
            pairs.append((variable, value))

        return pairs

    def _cast_value_to_type(self, variable: Variable, value: str):
        annotation = variable.annotation
        if annotation == str:
            return value
        if get_origin(annotation) == Literal:
            literals = [str(literal) for literal in annotation.__args__]
            return annotation.__args__[literals.index(value)]
        return annotation(value)

    def _populate_object(
        self, target_class: Type[Any], properties: dict[str, object], root: bool = True
    ) -> Any:
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
        for child, child_properties in children.items():
            child_class = annotations[child]
            current_object_properties[child] = self._populate_object(
                child_class, child_properties, root=False
            )

        if root:
            for key, value in current_object_properties.items():
                setattr(self, key, value)
            return self
        else:
            return target_class(**current_object_properties)

    @staticmethod
    def _get_class_property_annotation(target_class: Type[Any], property: str) -> Any:
        annotations = get_type_hints(target_class)
        if "." in property:
            current_class_property, child_class_property = property.split(
                ".", maxsplit=1
            )
            child_class = annotations[current_class_property]
            return Gingerino._get_class_property_annotation(
                child_class, child_class_property
            )

        try:
            return annotations[property]
        except KeyError:
            raise TemplateError(f"'{property}' is not valid")


T = TypeVar("T")


def parserino(type: Type[T], template: str, input: str) -> T:
    return Gingerino(type, template).parse(input)
