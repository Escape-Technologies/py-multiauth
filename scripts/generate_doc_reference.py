import json
import re
from typing import Any, Dict, List, TypeVar, Union
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader

from scripts.entities import (
    PropertyRequired,
    PropertyType,
    SchemaAnchor,
    SchemaDescription,
    SchemaEnum,
    SchemaObject,
    SchemaProperty,
)


# URL Formatting Functions
def format_url(url: str) -> str:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace('www.', '', 1)
    return f'[{domain}]({url})'


def replace_urls(text: str) -> str:
    url_pattern = re.compile(r'https?://[^\s]+')
    return url_pattern.sub(lambda match: format_url(match.group(0)), text)


T = TypeVar('T', bound=Union[Dict[Any, Any], List[Any]])


def remove_none_empty(data: T) -> T:
    """
    Recursively remove all None values and empty containers from dictionaries and lists.
    """
    if isinstance(data, dict):
        return {k: remove_none_empty(v) for k, v in data.items() if v is not None and v != '' and v != {} and v != []}  # type: ignore[return-value]
    if isinstance(data, list):
        return [remove_none_empty(v) for v in data if v is not None and v != '' and v != {} and v != []]  # type: ignore[return-value]
    return data


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
                    description=SchemaDescription(replace_urls(details.get('description', ''))),
                    reference=ref,
                )

            description = None
            kind = None
            examples = None
            title = None
            if '_doc' in defs:
                description = SchemaDescription(replace_urls(defs['_doc']['description']))
                kind = defs['_doc']['kind']
                examples = remove_none_empty(defs['_doc']['examples'])
                title = defs['_doc']['title']

            all_objects[object_name] = SchemaObject(
                name=object_name,
                anchor=object_name,
                description=description,
                properties=properties,
                kind=kind,
                examples=examples,
                title=title,
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


# Load JSON schema
with open('multiauth-schema.json', 'r') as file:
    json_schema = json.load(file)

processed_objects, processed_enums = SchemaModel(json_schema).get_results()

# Template Rendering
env = Environment(loader=FileSystemLoader('scripts/templates'), autoescape=True)
template = env.get_template('reference.md.jinja')
rendered_markdown = template.render(objects=processed_objects, enumerations=processed_enums)

# Save the Rendered Markdown
with open('../docs/docs/05-authentication/advanced/reference.mdx', 'w') as file:
    file.write(rendered_markdown)
