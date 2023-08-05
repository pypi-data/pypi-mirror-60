from .fields import Field, FieldTypes
from ..errors import ParseError

from dataclasses import dataclass, field
from typing import Any, List, Dict
import inspect


@dataclass
class DictField(Field):
    allowedTypes: List = field(default_factory=lambda: [FieldTypes.OBJECT])

    def __init__(self, fields: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = fields or {}
        for k, v in fields.items():
            setattr(self, k, v)

    def _getFields(self):
        return {
            f: theField
            for (f, theField) in filter(
                lambda k: isinstance(k[1], Field),
                inspect.getmembers(self),
            )
        }

    def parser(self, source: Dict):
        source = source or {}
        fields = self._getFields()
        if not fields:
            return source
        parameters = {}
        for name, parameter in fields.items():
            if (not parameter.optional) and (name not in source):
                raise ParseError(
                    message="Missing required field: {}".format(name),
                    statusCode=parameter.missingStatusCode,
                )
            parameters[name] = parameter.parse(
                source.get(name, parameter.default)
            )
        return parameters

    def serialize(self, dictValue):
        fields = self._getFields()
        if not fields:
            return dictValue
        result = {}

        for name, outField in fields.items():
            try:
                value = dictValue[name]
                name = getattr(outField, "serializeTo", name) or name

                try:
                    result[name] = outField.serialize(value)
                except:
                    result[name] = value
            except KeyError as k:
                if not outField.optional:
                    result[name] = None

        return result

    def describe(self):
        return {
            key: field.describe()
            for (key, field) in self._getFields().items()
        }


class PrefixDictField(DictField):
    """
    A dict field which matches any keys in the source
    starting with a given prefix, and parses the suffixes
    and values
    """

    def __init__(self, prefix: str, parseFromFunc=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = prefix
        self.parseFromFunc = self._parseFromFunc

    def _parseFromFunc(self, source):
        result = {}
        for k, v in source.items():
            if k.startswith(self.prefix):
                result[k[len(self.prefix):]] = v

        return self.parse(result)
