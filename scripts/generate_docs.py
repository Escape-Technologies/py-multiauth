import json
import re
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader

from scripts.entities import (
    ObjectDescription,
    PropertyDescription,
    PropertyRequired,
    PropertyType,
    SchemaAnchor,
    SchemaEnum,
    SchemaObject,
    SchemaProperty,
)

# Load JSON schema
with open('multiauth-schema.json', 'r') as file:
    json_schema = json.load(file)


# URL Formatting Functions
def format_url(url: str) -> str:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('www.', '', 1)
    return f'[{domain}]({url})'


def replace_urls(text: str) -> str:
    url_pattern = re.compile(r'https?://[^\s]+')
    return url_pattern.sub(lambda match: format_url(match.group(0)), text)


# Property Processing Function
def process_property(details: dict) -> tuple[SchemaAnchor | None, PropertyType | None, PropertyRequired]:
    if not isinstance(details, dict):
        raise ValueError(f'Property details take a dict as input: {type(details)}')

    ref: SchemaAnchor | None = details.get('$ref', '').split('/')[-1] or None
    prop_type: PropertyType | None = details.get('type')
    required = PropertyRequired(True)

    if 'const' in details:
        return None, PropertyType(f'Const[{details["const"]}]'), required

    if 'discriminator' in details:
        refs: set[SchemaAnchor | None] = set()
        prop_types: set[PropertyType | None] = set()
        for detail in [{'$ref': detail} for detail in details['discriminator']['mapping'].values()]:
            a, b, _ = process_property(detail)
            refs.add(a)
            prop_types.add(b)
        refs.discard(None)
        prop_types.discard(None)

        prop_type = PropertyType(' | '.join([str(prop_type) for prop_type in prop_types]))
        # TODO(antoine@escape.tech): Add support for multiple refs, currently returning None. cf. hack above
        return None, prop_type, required

    if 'anyOf' in details:
        refs = set()
        prop_types = set()
        for detail in details['anyOf']:
            a, b, _ = process_property(detail)
            refs.add(a)
            prop_types.add(b)
        refs.discard(None)
        prop_types.discard(None)

        if 'null' in prop_types:
            prop_types.remove(PropertyType('null'))
            required = PropertyRequired(False)

        if len(prop_types) > 1 or len(refs) > 1:
            raise ValueError(f'[anyOf] We do not support anyOf types with len > 1: {prop_types} {refs}')

        ref = next(iter(refs), None)
        prop_type = next(iter(prop_types), None)

        if ref is None and prop_type is None:
            prop_type = PropertyType('Any')

        if prop_type is None:
            raise ValueError(f'[anyOf] Property type cannot be None: {details}')

        return ref, prop_type, required

    if 'allOf' in details:
        if len(details['allOf']) > 1:
            raise ValueError(f'Cannot process allOf with more than one item: {details}')

        return process_property(details['allOf'][0])

    if prop_type == 'array':
        # Extract reference from 'items'
        return process_property(details['items'])

    if prop_type == 'object':
        # Extract reference from 'additionalProperties'
        ref, prop_type, required = process_property(details['additionalProperties'])
        return ref, PropertyType(f'Dict[string, {prop_type}]'), required

    prop_type = PropertyType(ref) if ref is not None else prop_type

    return SchemaAnchor(ref) if ref is not None else None, prop_type, required


class SchemaModel:
    json_schema: dict
    enums: dict[SchemaAnchor, SchemaEnum]
    objects: dict[SchemaAnchor, SchemaObject]

    def __init__(self, schema: dict):
        self.json_schema = schema
        self.enums = self.collect_enums(schema)
        self.objects = self.collect_objects()

    def extract_ref(self, details: dict) -> SchemaAnchor | None:
        item_ref = details.get('$ref', '').split('/')[-1]

        if not item_ref:
            return None

        if item_ref not in self.enums and item_ref not in self.objects:
            raise ValueError(f'Unknown reference: {item_ref}')

        return item_ref

    def collect_objects(self) -> dict[SchemaAnchor, SchemaObject]:
        all_objects = {}
        for object_name, defs in self.json_schema['$defs'].items():
            if 'enum' in defs:
                continue

            properties = {}

            for property_name, details in defs['properties'].items():
                ref, prop_type, required = process_property(details)
                if prop_type is None:
                    raise ValueError(f'Root property type cannot be None: {property_name, details}')
                properties[property_name] = SchemaProperty(
                    name=property_name,
                    type=prop_type,
                    required=PropertyRequired(required and property_name in defs.get('required', [])),
                    description=PropertyDescription(replace_urls(details.get('description', ''))),
                    reference=ref,
                )

            all_objects[object_name] = SchemaObject(
                name=object_name,
                anchor=object_name,
                description=ObjectDescription(replace_urls(defs.get('description', ''))),
                properties=properties,
            )

        return all_objects

    def get_results(self) -> tuple[list[dict], list[dict]]:
        return [obj.model_dump() for obj in self.objects.values()], [enum.model_dump() for enum in self.enums.values()]

    @staticmethod
    def collect_enums(schema: dict) -> dict[SchemaAnchor, SchemaEnum]:
        return {
            name: SchemaEnum(name=name, anchor=name, enum_values=defs['enum'])
            for name, defs in schema['$defs'].items()
            if 'enum' in defs
        }


processed_objects, processed_enums = SchemaModel(json_schema).get_results()

# Template Rendering
env = Environment(loader=FileSystemLoader('scripts/templates'), autoescape=True)
template = env.get_template('schema-property.md.jinja')
rendered_markdown = template.render(objects=processed_objects, enumerations=processed_enums)

# Save the Rendered Markdown
with open('docs/reference/entities.md', 'w') as file:
    file.write(rendered_markdown)
