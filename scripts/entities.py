from typing import NewType

from pydantic import BaseModel

PropertyName = NewType('PropertyName', str)
PropertyType = NewType('PropertyType', str)
PropertyRequired = NewType('PropertyRequired', bool)
PropertyDescription = NewType('PropertyDescription', str)

ObjectName = NewType('ObjectName', str)
ObjectDescription = NewType('ObjectDescription', str)

EnumName = NewType('EnumName', str)
EnumValue = NewType('EnumValue', str)

SchemaAnchor = NewType('SchemaAnchor', str)


class SchemaProperty(BaseModel):
    name: PropertyName
    type: PropertyType
    required: PropertyRequired
    description: PropertyDescription
    reference: SchemaAnchor | None


class SchemaObject(BaseModel):
    name: ObjectName
    anchor: SchemaAnchor
    description: ObjectDescription
    properties: dict[PropertyName, SchemaProperty]


class SchemaEnum(BaseModel):
    name: EnumName
    anchor: SchemaAnchor
    enum_values: list[EnumValue]
