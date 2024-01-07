import json

from jinja2 import Environment, FileSystemLoader

# Load your JSON schema into a Python dictionary
with open('multiauth-schema.json', 'r') as file:
    json_schema = json.load(file)


# Process the JSON schema to prepare data for the template
def process_schema(schema: dict) -> list:
    definitions = []
    for def_name, def_properties in schema['$defs'].items():
        properties = []
        for prop_name, prop_details in def_properties.get('properties', {}).items():
            prop_info = {
                'name': prop_name,
                'type': prop_details.get('type', 'N/A'),
                'required': prop_name in def_properties.get('required', []),
                'description': prop_details.get('description', ''),
                'reference': prop_details.get('$ref', '').split('/')[-1] if '$ref' in prop_details else '',
            }
            properties.append(prop_info)

        definition_info = {
            'name': def_name,
            'anchor': def_name,
            'description': def_properties.get('description', 'No Description.'),
            'type': def_properties.get('type', 'N/A'),
            'properties': properties,
        }
        definitions.append(definition_info)
    return definitions


processed_data = process_schema(json_schema)

# Set up the Jinja environment and load the template
env = Environment(loader=FileSystemLoader('scripts/templates'), autoescape=True)
template = env.get_template('schema-property.md.jinja')

# Render the template with the processed data
rendered_markdown = template.render(definitions=processed_data)

# Save the rendered Markdown
with open('docs/reference/reference.md', 'w') as file:
    file.write(rendered_markdown)
