import string

from .fields import Field, FieldTypes
from ..errors import ParseError

from dataclasses import dataclass, field
from typing import Any, List, Dict


@dataclass
class StringField(Field):
    """
    A generic string parameter
    """
    allowedTypes: List = field(default_factory=lambda: [FieldTypes.STRING])

    def parser(self, value):
        value = super().parser(value)
        if not isinstance(value, str):
            raise ParseError(message="\"{}\" is not a string".format(value))
        return value


@dataclass
class EnumeratedStringField(Field):
    """
    A string parameter which must be one of a particular set of values
    """
    allowedTypes: List = field(default_factory=lambda: [FieldTypes.STRING])
    allowedValues: List = field(default_factory=lambda: [])

    def parser(self, value):
        originalValue = value
        value = super().parser(value)
        if value not in self.allowedValues:
            raise ParseError(
                message=
                f"\"{originalValue}\" is not in {str(self.allowedValues)}"
            )
        return value

    def describe(self):
        doc = super().describe()
        doc["allowedValues"] = self.allowedValues
        return doc


@dataclass
class NoWhitespaceStringField(StringField):
    """
    A string field where leading/trailing whitespace
    should be trimmed.
    """

    def normalizer(self, value):
        value = super().normalizer(value)
        return value.strip()


@dataclass
class NonBlankStringField(NoWhitespaceStringField):
    def parser(self, value):
        value = super().parser(value)
        if not value:
            raise ParseError(message="Cannot be blank")
        return value


@dataclass
class EmailField(NonBlankStringField):
    def parser(self, value):
        value = super().parser(value)
        if "@" not in value:
            raise ParseError(message=f"{value} is not a valid email address", )
        return value


@dataclass
class UsernameField(NonBlankStringField):
    def parser(self, value):
        value = super().parser(value)

        if any([c in value for c in string.whitespace]):
            raise ParseError("Usernames must not contain whitespace")

        return value
