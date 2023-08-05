from .fields import Field, FieldTypes
from ..errors import ParseError

from dataclasses import dataclass, field
from typing import Any, List, Dict


@dataclass
class ListField(Field):
    def __init__(self, elementField, **kwargs):
        super().__init__(**kwargs)
        self.elementField = elementField
        self.default = []

    def parser(self, source):
        if not source:
            return []
        parsed = []
        for value in source:
            parsed.append(self.elementField.parser(value))
        return parsed

    def serialize(self, values):
        result = []
        if not values:
            return result
        for value in values:
            try:
                result.append(self.elementField.serialize(value))
            except Exception as e:
                result.append(value)

        return result