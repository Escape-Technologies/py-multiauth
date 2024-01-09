"""
poetry run python scripts/generate_docs.py
"""
import json

from jinja2 import Environment, FileSystemLoader

# Load your JSON schema into a Python dictionary
with open('multiauth-schema.json', 'r') as file:
    json_schema = json.load(file)


import re
from urllib.parse import urlparse


def process_schema(schema: dict) -> list:
    url_pattern = re.compile(r'https?://[^\s]+')

    def format_url(url: str) -> str:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        # Remove 'www.' if it exists in the domain name
        if domain.startswith('www.'):
            domain = domain[4:]
        return f'[{domain}]({url})'

    def replace_urls(text: str) -> str:
        return url_pattern.sub(lambda match: format_url(match.group(0)), text)

    definitions = []
    for def_name, def_properties in schema['$defs'].items():
        properties = []
        for prop_name, prop_details in def_properties.get('properties', {}).items():
            item_ref = prop_details.get('items', {}).get('$ref', '').split('/')[-1]
            # Determine if the property is an array
            if prop_details.get('type') == 'array':
                # Extract the type of items in the array
                prop_type = f'{item_ref}[]' if item_ref else 'array'
            else:
                prop_type = prop_details.get('type', 'N/A')

            is_required = prop_name in def_properties.get('required', [])
            description = replace_urls(prop_details.get('description', ''))

            prop_info = {
                'name': prop_name,
                'type': prop_type,
                'required': is_required,
                'description': description,
                'reference': item_ref if item_ref else '',
            }
            properties.append(prop_info)

        # Sort properties: required first, non-referenced second, then alphabetically
        properties.sort(key=lambda x: (not x['required'], x['reference'] != '', x['name'].lower()))

        description = replace_urls(def_properties.get('description', 'No Description.'))
        definition_info = {
            'name': def_name,
            'anchor': def_name,
            'description': description,
            'type': def_properties.get('type', 'N/A'),
            'properties': properties,
        }
        definitions.append(definition_info)
    return definitions


processed_data = process_schema(json_schema)


processed_data = process_schema(json_schema)

# Set up the Jinja environment and load the template
env = Environment(loader=FileSystemLoader('scripts/templates'), autoescape=True)
template = env.get_template('schema-property.md.jinja')

# Render the template with the processed data
rendered_markdown = template.render(definitions=processed_data)

# Save the rendered Markdown
with open('docs/reference/entities.md', 'w') as file:
    file.write(rendered_markdown)
