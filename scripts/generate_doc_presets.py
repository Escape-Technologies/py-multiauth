import json
from typing import Any, Dict, List, TypeVar, Union

import yaml
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
from pydantic import BaseModel

from multiauth.lib.presets.base import PresetType
from scripts.entities import EnumName, ObjectName, SchemaDescription, SchemaEnum, SchemaObject, SchemaTitle
from scripts.generate_doc_reference import SchemaModel

all_examples: dict[PresetType, list[dict]] = {}

T = TypeVar('T', bound=Union[Dict[str, Any], List[Any], Any])


class PresetResult(BaseModel):
    name: ObjectName
    description: SchemaDescription
    title: SchemaTitle
    examples: list
    preset: SchemaObject
    objects: list[SchemaObject]
    enums: list[SchemaEnum]


# Custom filter to convert JSON to YAML
def json_to_yaml(json_data: dict) -> Markup:
    yaml_text = yaml.dump(json_data, default_flow_style=False, sort_keys=False, indent=4)
    return Markup(yaml_text)


def sort_keys(obj: T) -> T:
    def sort_criteria(key: str) -> tuple:
        # Assign priorities based on the key name and type of value
        priority = 10  # default priority for other keys
        if 'type' in key or 'name' in key:
            priority = 1
        elif 'url' in key:
            priority = 2
        elif isinstance(obj[key], (str, int, float, bool, type(None))):  # type: ignore[call-overload]
            priority = 3
        elif 'request' in key:
            priority = 4
        elif 'inject' in key:
            priority = 5
        elif 'extract' in key:
            priority = 6
        return (priority, key)

    if isinstance(obj, dict):
        # Sort the keys of the dictionary based on the sort criteria
        sorted_keys = sorted(obj.keys(), key=sort_criteria)
        return {k: sort_keys(obj[k]) for k in sorted_keys}  # type: ignore[return-value]
    if isinstance(obj, list):
        # Apply the sorting function recursively to each item in the list
        return [sort_keys(item) for item in obj]  # type: ignore[return-value]

    # If obj is not a list or dict, return it as is
    return obj


# Load JSON schema
with open('multiauth-schema.json', 'r') as f:
    json_schema = json.load(f)

schema = SchemaModel(json_schema)


results = list[PresetResult]()

for model in schema.objects.values():
    if model.kind != 'preset':
        continue
    preset = model
    objects: dict[ObjectName, SchemaObject] = {}
    enums: dict[EnumName, SchemaEnum] = {}

    # Collect all objects and enums referenced by the preset
    for prop in preset.properties.values():
        if prop.reference is not None:
            if prop.reference in schema.enums:
                enum_res = schema.enums[prop.reference]
                enums[enum_res.name] = enum_res
            else:
                object_res = schema.objects[prop.reference]
                objects[object_res.name] = object_res

    # Collect additional enums that are referenced by the objects referenced by the preset
    for obj in objects.values():
        for prop in obj.properties.values():
            if prop.reference is not None:
                if prop.reference in schema.enums:
                    enum_res = schema.enums[prop.reference]
                    enums[enum_res.name] = enum_res

    examples = []
    if preset.examples:
        for example in preset.examples:
            examples.append({'preset': sort_keys(example)})

    results.append(
        PresetResult(
            name=preset.name,
            description=preset.description or SchemaDescription(''),
            title=preset.title or SchemaTitle(''),
            examples=examples,
            preset=preset,
            objects=list(objects.values()),
            enums=list(enums.values()),
        ),
    )


# Load Jinja environment
env = Environment(loader=FileSystemLoader('scripts/templates'), autoescape=True)
env.filters['json_to_yaml'] = json_to_yaml
template = env.get_template('preset.md.jinja')

# Render and write each preset to a separate file
for result in results:
    rendered_content = template.render(result=result)
    with open(f'../docs/docs/05-authentication/{result.title.replace(" ", "").lower()}.md', 'w') as f:
        f.write(rendered_content)
