from datetime import date, timedelta
from enum import Enum
from os import PathLike

import yaml


class FieldType(Enum):
    MAPPING = 0
    CONST = 1
    TEXT = 2
    DATE = 3


class Field:
    def __init__(self, name: str, field_type: FieldType, **kwargs):
        self.name = name
        self.field_type = field_type
        if field_type == FieldType.MAPPING:
            self.mapping = kwargs.get("mapping")
            assert self.mapping is not None
        elif field_type == FieldType.CONST:
            self.value = kwargs.get("value")
            assert self.value is not None
        elif field_type == FieldType.DATE:
            if kwargs.get("today"):
                plus = kwargs.get("plus")
                today = date.today()
                if plus is not None:
                    self.value = today + timedelta(days=int(plus))
                else:
                    self.value = str(today)
            else:
                self.value = self.value
        else:
            self.field_type = FieldType.TEXT
            self.value = kwargs.get("default")
            if kwargs.get("options"):
                self.options = kwargs.get("options")
            else:
                self.options = []
            assert self.value is not None

def read_fields_file(fields_file: PathLike) -> dict[str, Field]:
    fields = yaml.safe_load(open(fields_file, "rt", encoding="utf-8"))
    result = {}
    for key,value in fields["mappings"].items():
        result[key] = Field(name=key, field_type=FieldType.MAPPING, mapping=value)
    for key,value in fields["constants"].items():
        result[key] = Field(name=key, field_type=FieldType.CONST, value=value)
    for key,value in fields["editables"].items():
        type = value.get("type")
        if type == "date":
            result[key] = Field(name=key, field_type=FieldType.DATE, **value)
        else:
            result[key] = Field(name=key, field_type=FieldType.TEXT, **value)
    return result
