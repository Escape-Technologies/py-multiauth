import enum
from typing import NewType

from pydantic import BaseModel

PropertyName = NewType('PropertyName', str)
PropertyType = NewType('PropertyType', str)
PropertyRequired = NewType('PropertyRequired', bool)

ObjectName = NewType('ObjectName', str)

EnumName = NewType('EnumName', str)
EnumValue = NewType('EnumValue', str)

SchemaAnchor = NewType('SchemaAnchor', str)
SchemaTitle = NewType('SchemaTitle', str)
SchemaDescription = NewType('SchemaDescription', str)


class SchemaKind(enum.StrEnum):
    preset = 'preset'


class SchemaProperty(BaseModel):
    name: PropertyName
    type: PropertyType
    required: PropertyRequired
    description: SchemaDescription
    reference: SchemaAnchor | None


class SchemaObject(BaseModel):
    name: ObjectName
    anchor: SchemaAnchor
    properties: dict[PropertyName, SchemaProperty]
    description: SchemaDescription | None
    title: SchemaTitle | None
    examples: list | None
    kind: SchemaKind | None


class SchemaEnum(BaseModel):
    name: EnumName
    anchor: SchemaAnchor
    enum_values: list[EnumValue]
