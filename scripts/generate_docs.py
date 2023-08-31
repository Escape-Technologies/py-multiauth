"""Generate Docs in Check."""

import json
from copy import deepcopy
from typing import List, Dict, Any, cast, TypedDict, Optional
from importlib import resources

from jinja2 import Environment, FileSystemLoader, select_autoescape

from multiauth import static

env = Environment(loader=FileSystemLoader('scripts/templates'), autoescape=select_autoescape())


class AuthProperty(TypedDict):

    """The dictionary that contains all necessary information to document everything."""

    name: str
    optional: bool
    type: str
    description: str
    value: Optional[str]
    enum: Optional[List[str]]


AuthName = str
ParameterName = str
AuthParameter = Dict[ParameterName, AuthProperty]
AuthSchema = Dict[AuthName, List[Dict[AuthName, AuthParameter]]]
SubSchema = Dict[AuthName, AuthParameter]


def get_example(schema: Dict) -> Any:
    """From the schema of a parameter find an example."""

    if 'enum' in schema:
        return schema['enum'][0]
    if schema['type'] in ['number', 'string']:
        return '**value**'
    if schema['type'] == 'object':
        example = {}
        if 'additionalProperties' in schema and isinstance(schema['additionalProperties'], Dict):
            example['**value**'] = get_example(schema['additionalProperties'])
        for field_name, field in schema['properties'].items():
            example[field_name] = get_example(field)
        return example
    if schema['type'] == 'array':
        return [get_example(schema['items'])]

    raise Exception(f'The type {schema["type"]} is not handled by the script')


# pylint: disable=too-many-statements, too-many-locals, too-many-branches
def generate_auth_docs() -> None:
    """Generates authentication schemas documentation."""

    # Load the templeate
    template = env.get_template('docs_auth_template.md')

    # Load the json schema from static
    with resources.open_text(static, 'auth_schema.json') as f:
        json_schema = json.load(f)

    # The schema layout
    auth_schemas: AuthSchema = {}

    # A list which shows which authentication techniques have an optional parameter
    has_optional: List[bool] = [False for _ in json_schema]

    # The JSON schema for every authentication scheme
    jsonschema: Dict = {'users': {'user1': {'auth': 'schema1'}}, 'auth': {'schema1': {}}}

    # All the JSON schemas
    jsonschemas: List[Dict[str, str]] = []

    # A counter to fill the lists
    count = 0

    # Now we have to build the data structure to use to render the template
    for auth_schema in json_schema.values():

        # The subschemas
        sub_schema: SubSchema = {}

        auth_name = cast(AuthName, auth_schema['_escapeUI']['label'])
        auth_schemas.setdefault(auth_name, [{auth_name: {}}])

        if "oneOf" in auth_schema["authSchema"]:
            # here we are in the oauth case
            # we want to create a subschema for each possible values of the grant_type
            # and store in the whitelist{grant_type: required_fields}
            whitelist = {}
            for todo in auth_schema["authSchema"]["oneOf"]:
                property_name = next(iter(todo['properties'].keys()))
                property_value = todo['properties'][property_name]['const']
                schema_name = auth_name + ' (' + property_name + ' : ' + property_value + ')'
                sub_schema.setdefault(schema_name, {})
                whitelist[schema_name] = todo['required']
                sub_schema[schema_name].setdefault(
                    property_name,
                    AuthProperty({
                        'name': property_name,
                        'optional': False,
                        'type': 'string',
                        'description': '',
                        'value': property_value,
                        'enum': '',
                    })
                )

        for name, auth_property in auth_schema['authSchema']['properties'].items():
            if name == 'options':
                has_optional[count] = True
                for optional_name, optional_property in auth_property['properties'].items():
                    property_name = cast(ParameterName, optional_property['_escapeUI']['label'])
                    auth_schemas[auth_name][0][auth_name].setdefault(
                        optional_name, AuthProperty({
                            'name': property_name,
                            'optional': True,
                            'type': '',
                            'description': '',
                            'value': None,
                            'enum': None,
                        })
                    )
                    auth_schemas[auth_name][0][auth_name][optional_name]['type'] = optional_property['type']
                    auth_schemas[auth_name][0][auth_name][optional_name]['description'] = optional_property['description']
                    if optional_property.get('enum') is not None:
                        auth_schemas[auth_name][0][auth_name][optional_name]['enum'] = optional_property['enum']

            elif name == 'allOf':
                for condition in auth_schema['authSchema']['properties'][name]:
                    property_name = next(iter(condition['if']['properties']))
                    property_value = condition['if']['properties'][property_name]['const']
                    schema_name = auth_name + ' (' + property_name + ' : ' + property_value + ')'
                    sub_schema.setdefault(schema_name, {})

                    # Now we have to create the subschema
                    # First we have to create the parameter we have now
                    sub_schema[schema_name].setdefault(
                        property_name,
                        AuthProperty({
                            'name': auth_schemas[auth_name][0][auth_name][property_name]['name'],
                            'optional': auth_schemas[auth_name][0][auth_name][property_name]['optional'],
                            'type': auth_schemas[auth_name][0][auth_name][property_name]['type'],
                            'description': auth_schemas[auth_name][0][auth_name][property_name]['description'],
                            'value': property_value,
                            'enum': auth_schemas[auth_name][0][auth_name][property_name]['enum'],
                        })
                    )

                    for sub_name, sub_auth_property in condition['then']['properties'].items():
                        property_name = cast(ParameterName, sub_auth_property['_escapeUI']['label'])
                        sub_schema[schema_name].setdefault(
                            sub_name, AuthProperty({
                                'name': property_name,
                                'optional': False,
                                'type': '',
                                'description': '',
                                'value': None,
                                'enum': None,
                            })
                        )

                        sub_schema[schema_name][sub_name]['type'] = sub_auth_property['type']
                        sub_schema[schema_name][sub_name]['description'] = sub_auth_property['description']
                        if sub_auth_property.get('enum') is not None:
                            sub_schema[schema_name][sub_name]['enum'] = sub_auth_property['enum']

                        if sub_auth_property.get('title') is not None:
                            sub_schema[schema_name][sub_name]['value'] = sub_auth_property['title']

            else:
                property_name = cast(ParameterName, auth_property['_escapeUI']['label'])
                auth_schemas[auth_name][0][auth_name].setdefault(
                    name, AuthProperty({
                        'name': property_name,
                        'optional': False,
                        'type': '',
                        'description': '',
                        'value': None,
                        'enum': None,
                    })
                )
                auth_schemas[auth_name][0][auth_name][name]['type'] = auth_property['type']
                auth_schemas[auth_name][0][auth_name][name]['description'] = auth_property['description']
                if auth_property.get('enum') is not None:
                    auth_schemas[auth_name][0][auth_name][name]['enum'] = auth_property['enum']

                if auth_property.get('title') is not None:
                    auth_schemas[auth_name][0][auth_name][name]['value'] = auth_property['title']

        the_temp: Dict = {}
        for schema_name, schema_properties in sub_schema.items():
            original_schema = deepcopy(auth_schemas[auth_name][0][auth_name])
            if "oneOf" in auth_schema["authSchema"]:
                # handle oneOf to only write the required properties
                original_schema = {k: v for k, v in original_schema.items() if k in whitelist[schema_name] or v.get("optional")}
            for schema_property_name, schema_property_value in schema_properties.items():
                if schema_property_name in original_schema:
                    original_schema[schema_property_name] = schema_property_value
                else:
                    original_schema.setdefault(schema_property_name, schema_property_value)
                    the_temp.setdefault(schema_property_name, schema_property_value)

            auth_schemas[auth_name].append({schema_name: original_schema})

        auth_schemas[auth_name][0][auth_name].update(the_temp)

        # Now we have to build the json schema for every one of the authentication techniques
        _json_schema = deepcopy(jsonschema)

        # First we have to build the user part of the schema
        if auth_name == 'No authentification':
            user_name = 'public'
            _json_schema['users'][user_name] = _json_schema['users']['user1']
            del _json_schema['users']['user1']
        else:
            user_name = 'user1'

        for name, auth_property in auth_schema['userSchema']['properties'].items():
            if name == 'auth':
                continue
            if auth_property['type'] == 'object':
                _json_schema['users'][user_name][name] = {'**name**': '**value**'}
            else:
                _json_schema['users'][user_name][name] = '**' + auth_property['type'] + '**'

        if auth_schema['userSchema'].get('additionalProperties'):
            _json_schema['users'][user_name]['**username**'] = '**admin**'
            _json_schema['users'][user_name]['**password**'] = '**1234**'

        # Now we will build the auth part of the schema
        temp: Dict = {}

        if has_optional[count]:
            _json_schema['auth']['schema1']['options'] = {}
        for schema in auth_schemas[auth_name]:
            for schema_name, properties in schema.items():
                _new_json_schema = deepcopy(_json_schema)
                for name, auth_property in properties.items():
                    if not auth_property['optional']:
                        if auth_property['value'] is not None:
                            _new_json_schema['auth']['schema1'][name] = auth_property['value']
                        else:
                            _new_json_schema['auth']['schema1'][name] = '**' + auth_property['type'] + '**'

                    else:
                        if auth_property['value'] is not None:
                            _new_json_schema['auth']['schema1']['options'][name] = auth_property['value']
                        elif auth_property['type'] == 'object':
                            _new_json_schema['auth']['schema1']['options'][name] = {'**name**': '**value**'}
                        else:
                            _new_json_schema['auth']['schema1']['options'][name] = '**' + auth_property['type'] + '**'
                # This is simply to rearange the Dict (althought there is no order) so that options is at the end
                if _new_json_schema['auth']['schema1'].get('options') is not None:
                    _temp = deepcopy(_new_json_schema['auth']['schema1']['options'])
                    del _new_json_schema['auth']['schema1']['options']
                    _new_json_schema['auth']['schema1']['options'] = _temp
                temp[schema_name] = json.dumps(_new_json_schema, indent=4, sort_keys=False)

        # Add the manual shorthand
        if auth_name == 'Manual':
            shorthand = {"headers": {'**name**': '**value**'}}
            temp['Manual (shorthand)'] = json.dumps(shorthand, indent=4, sort_keys=False)
            temp['Manual (standard)'] = temp['Manual']

        jsonschemas.append(temp)
        count += 1

    auth_documentation = template.render(auth_schema=auth_schemas, optional=has_optional, json_schema=jsonschemas)

    with open('docs/index.md', 'w+', encoding='utf-8') as f:
        f.write(auth_documentation)


if __name__ == '__main__':
    generate_auth_docs()
