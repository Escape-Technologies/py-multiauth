"""Generate authrc from -H or cURL."""

import base64
import json
from typing import Optional, cast
from urllib.parse import parse_qs

import graphql

from multiauth.config import PY_MULTIAUTH_LOGGER as logger
from multiauth.types.http import HTTPMethod
from multiauth.types.main import AuthTech, RCFile
from multiauth.utils import uncurl

POTENTIAL_FIELD_NAME = ['token']


def urlencoded_to_json(data: str | None) -> str | None:
    """This function transforms data in application/x-www-form-urlencoded to json data."""

    if data is None:
        return None

    new_form = parse_qs(data)
    json_data: dict = {}
    for name, value in new_form.items():
        if len(value) == 1:
            json_data[name] = value[0]
        else:
            json_data[name] = value

    return json.dumps(json_data)


def deserialize_headers(headers: dict[str, str] | list[str] | str) -> dict[str, str]:
    """Convert headers to standard format."""

    res: dict[str, str] = {}

    if isinstance(headers, str):
        headers = [headers]

    if isinstance(headers, list):

        for header in headers:
            header_split = header.split(':', 1)
            res[header_split[0].strip()] = header_split[1].strip()

        return res

    return headers


def _manual_fill(headers: dict[str, str] | list[str] | str) -> RCFile:
    """Serialize raw headers in "manual" auth format."""

    headers_dict = deserialize_headers(headers)

    auth_name: str = 'manual_headers'

    rcfile: RCFile = {
        'auth': {
            auth_name: {
                'tech': AuthTech.MANUAL,
            }
        },
        'users': {
            'manual_user': {
                'headers': headers_dict,
                'auth': auth_name
            }
        },
    }

    return rcfile


def _basic_fill(headers: dict[str, str], authorization_header: str) -> RCFile:
    """Convert basic headers to curl."""

    # Then the type of authentification is basic

    decoded_value: str = cast(str, base64.b64decode(authorization_header.split(' ')[1]))
    username, password = decoded_value.split(':', 1)

    # The JSON schema for every authentication scheme
    rcfile: RCFile = {
        'users': {
            'user_basic': {
                'auth': 'auth_basic',
                'username': username,
                'password': password,
            }
        },
        'auth': {
            'auth_basic': AuthTech.BASIC
        },
    }

    optional_headers: dict = {}
    for key, value in headers.items():
        if 'authorization' not in key.lower():
            optional_headers[key] = value

    if optional_headers:
        rcfile['auth']['auth_basic']['options'] = {'headers': optional_headers}

    return rcfile


def _rest_fill(rest_document: dict, url: str, method: HTTPMethod, headers: dict[str, str]) -> RCFile:
    """This function fills the rest file."""

    # The JSON schema for every authentication scheme
    rcfile: RCFile = {
        'users': {
            'user1': {
                'auth': 'schema1'
            }
        },
        'auth': {
            'schema1': {}
        },
    }

    rcfile['users']['user1'].update(rest_document)
    rcfile['auth']['schema1']['tech'] = 'rest'
    rcfile['auth']['schema1']['url'] = url
    rcfile['auth']['schema1']['method'] = method
    rcfile['auth']['schema1']['options'] = {'headers': headers}

    return rcfile


def _graphql_fill(graphql_document: dict, url: str, method: HTTPMethod, headers: dict[str, str], variables: dict = None) -> RCFile:
    """This function fills the graphql escaperc file."""

    # The JSON schema for every authentication scheme
    rcfile: RCFile = {'users': {'user1': {'auth': 'schema1'}}, 'auth': {'schema1': {}}}

    rcfile['auth']['schema1']['tech'] = 'graphql'

    rcfile['auth']['schema1']['url'] = url
    rcfile['auth']['schema1']['method'] = method

    # Now we need to start finding the information about the mutation
    mutation_name = graphql_document['definitions'][0]['selection_set']['selections'][0]['name']['value']
    rcfile['auth']['schema1']['mutation_name'] = mutation_name

    # Now we need to get the user information
    credentials: dict = {}
    if variables and graphql_document['definitions'][0]['variable_definitions']:
        for variable in graphql_document['definitions'][0]['variable_definitions']:
            variable_name = variable['variable']['name']['value']
            if variable_name in variables:
                credentials[variable_name] = variables[variable_name]

    else:
        arguments = graphql_document['definitions'][0]['selection_set']['selections'][0]['arguments']
        if isinstance(arguments, list):
            for argument in arguments:
                if argument['value'].get('fields') is None:
                    credentials[argument['name']['value']] = argument['value']['value']
                else:
                    credentials[argument['name']['value']] = {}
                    for input_object_field in argument['value']['fields']:
                        credentials[argument['name']['value']][input_object_field['name']['value']] = input_object_field['value']['value']

    # Now regarding the field
    mutation_fields = graphql_document['definitions'][0]['selection_set']['selections'][0]['selection_set']['selections']
    for field in mutation_fields:
        if field['name']['value'].lower() in POTENTIAL_FIELD_NAME:
            rcfile['auth']['schema1']['mutation_field'] = field['name']['value']
            break

    rcfile['users']['user1'].update(credentials)

    rcfile['auth']['schema1']['options'] = {}
    rcfile['auth']['schema1']['options']['operation'] = graphql_document['definitions'][0]['operation']

    if headers:
        rcfile['auth']['schema1']['options']['headers'] = headers

    return rcfile


#pylint: disable=too-many-branches, too-many-statements
def curl_to_escaperc(curl: str) -> Optional[RCFile]:
    """This function transforms the curl request to an escaperc file."""

    # First we uncurl
    parsed_content = uncurl(curl)

    # First thing we have to check if in the headers, there is a basic authentication or a token already
    for header_key, header_value in parsed_content.headers.items():
        if 'authorization' in header_key.lower():
            if 'basic' in header_value.lower():
                logger.info('Type of authetication detected: Basic')
                return _basic_fill(parsed_content.headers, header_value)

    # Then we check if its REST or GraphQL authentication: check if the data that we have is graphql data
    query: dict = {}
    rcfile = RCFile({'auth': {}, 'users': {}})

    try:
        if parsed_content.data is not None:
            query = json.loads(parsed_content.data)
    except Exception:
        logger.debug('The `data` attribute of the cURL is not JSONable')

    if query:
        if query.get('query') is not None:
            logger.info('Type of authetication detected: GraphQL')
            graphql_tree = graphql.parse(query['query']).to_dict()
            if query.get('variables') is not None:
                rcfile = _graphql_fill(graphql_tree, parsed_content.url, parsed_content.method, parsed_content.headers, query['variables'])
            else:
                rcfile = _graphql_fill(graphql_tree, parsed_content.url, parsed_content.method, parsed_content.headers)

        else:
            logger.info('Type of authetication detected: REST')
            rcfile = _rest_fill(query, parsed_content.url, parsed_content.method, parsed_content.headers)

    else:
        # If we reached this else then the request sent is not being sent as application/json and is being sent as something else
        # Most probably it is an application/x-www-form-urlencoded format
        # Convert this format to json
        json_data = urlencoded_to_json(parsed_content.data)

        new_query: dict = {}
        try:
            if json_data is not None:
                new_query = json.loads(json_data)
        except Exception:
            logger.debug('The `data` attribute of the cURL is not JSONable so it is not sent as application/x-www-form-urlencoded')

        if new_query:
            if new_query.get('query') is not None:
                logger.info('Type of authetication detected: GraphQL')
                graphql_tree = graphql.parse(new_query['query']).to_dict()
                if new_query.get('variables') is not None:
                    rcfile = _graphql_fill(graphql_tree, parsed_content.url, parsed_content.method, parsed_content.headers, new_query['variables'])
                else:
                    rcfile = _graphql_fill(graphql_tree, parsed_content.url, parsed_content.method, parsed_content.headers)

            else:
                # Then the authentication type is rest
                logger.info('Type of authetication detected: REST')
                rcfile = _rest_fill(new_query, parsed_content.url, parsed_content.method, parsed_content.headers)

        else:
            return None

    return rcfile
