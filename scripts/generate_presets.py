import json

import yaml
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

from multiauth.lib.presets.base import PresetType
from scripts.entities import SchemaEnum, SchemaObject
from scripts.generate_docs import SchemaModel

all_examples: dict[PresetType, list[dict]] = {}


class PresetResult(BaseModel):
    type: PresetType
    examples: list[dict]
    preset: SchemaObject
    objects: list[SchemaObject]
    enums: list[SchemaEnum]


# Custom filter to convert JSON to YAML
def json_to_yaml(json_data: dict) -> str:
    return yaml.dump(json_data, default_flow_style=False, sort_keys=False)


# Load JSON schema
with open('multiauth-schema.json', 'r') as f:
    json_schema = json.load(f)


def get_preset(preset_type: PresetType, model: SchemaModel) -> SchemaObject:
    for obj in model.objects.values():
        for prop in obj.properties.values():
            if preset_type in prop.type:
                return obj

    raise ValueError(f'Could not find model for preset type: {preset_type}')


model = SchemaModel(json_schema)


results = list[PresetResult]()

for preset_type, examples in all_examples.items():
    preset = get_preset(preset_type, model)
    objects: list[SchemaObject] = []
    enums: list[SchemaEnum] = []
    for prop in preset.properties.values():
        if prop.reference is not None:
            if prop.reference in model.enums:
                enums.append(model.enums[prop.reference])
            else:
                objects.append(model.objects[prop.reference])

    results.append(
        PresetResult(
            type=preset_type,
            examples=examples,
            preset=preset,
            objects=objects,
            enums=enums,
        ),
    )


# Load Jinja environment
env = Environment(loader=FileSystemLoader('scripts/templates'), autoescape=True)
env.filters['json_to_yaml'] = json_to_yaml
template = env.get_template('preset.md.jinja')

# Render and write each preset to a separate file
for result in results:
    rendered_content = template.render(result=result)
    with open(f'docs/presets/{result.type}.md', 'w') as f:
        f.write(rendered_content)
