import json

from jinja2 import Template

# Load your JSON schema into a Python dictionary
with open('multiauth-schema.json', 'r') as file:
    json_schema = json.load(file)

# Load the Jinja template (assuming the above template is saved as 'schema_template.md.jinja')
with open('scripts/templates/schema-property.md.jinja', 'r') as file:
    template = Template(file.read())

# Render the template with the schema
rendered_markdown = template.render(schema=json_schema)

# You can then save this Markdown or display it as needed
with open('docs/reference/reference.md', 'w') as file:
    file.write(rendered_markdown)
