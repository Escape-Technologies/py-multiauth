"""Generate authrc from -H or cURL."""

import base64
import json
from typing import Dict, List, Optional, Union, cast
from urllib.parse import parse_qs

import graphql

from multiauth.entities.http import HTTPMethod
from multiauth.entities.main import AuthTech, RCFile
from multiauth.utils import setup_logger, uncurl

POTENTIAL_FIELD_NAME = ['token']

LOGGER = setup_logger()


def urlencoded_to_json(data: Optional[str]) -> Optional[str]:
    """This function transforms data in application/x-www-form-urlencoded to json data."""

    if data is None:
        return None

    new_form = parse_qs(data)
    json_data: Dict = {}
    for name, value in new_form.items():
        if len(value) == 1:
            json_data[name] = value[0]
        else:
            json_data[name] = value

    return json.dumps(json_data)


def deserialize_headers(headers: Union[Dict[str, str], List[str], str]) -> Dict[str, str]:
    """Convert headers to standard format."""

    res: Dict[str, str] = {}

    if isinstance(headers, str):
        headers = [headers]

    if isinstance(headers, list):
        for header in headers:
            header_split = header.split(':', 1)
            res[header_split[0].strip()] = header_split[1].strip()

        return res

    return headers


def _manual_fill(headers: Union[Dict[str, str], List[str], str]) -> RCFile:
    """Serialize raw headers in "manual" auth format."""

    headers_dict = deserialize_headers(headers)

    auth_name: str = 'manual_headers'

    return RCFile(
        {
            'auth': {
                auth_name: {
                    'tech': AuthTech.MANUAL.value,
                },
            },
            'users': {'manual_user': {'headers': headers_dict, 'auth': auth_name}},
        },
    )


def _basic_fill(
    headers: Dict[str, str],
    authorization_header: str,
) -> RCFile:
    """Convert basic headers to curl."""

    # Then the type of authentification is basic

    decoded_value: str = cast(str, base64.b64decode(authorization_header.split(' ')[1]))
    username, password = decoded_value.split(':', 1)

    # The JSON schema for every authentication scheme
    rcfile = RCFile(
        {
            'users': {
                'user_basic': {
                    'auth': 'auth_basic',
                    'username': username,
                    'password': password,
                },
            },
            'auth': {'auth_basic': {'tech': AuthTech.BASIC.value}},
        },
    )

    optional_headers: Dict = {}
    for key, value in headers.items():
        if 'authorization' not in key.lower():
            optional_headers[key] = value

    if optional_headers:
        rcfile['auth']['auth_basic']['options'] = {'headers': optional_headers}

    return rcfile


def _rest_fill(
    rest_document: Dict,
    url: str,
    method: HTTPMethod,
    headers: Dict[str, str],
) -> RCFile:
    """This function fills the rest file."""

    # The JSON schema for every authentication scheme
    return RCFile(
        {
            'users': {'user1': {'auth': 'schema1', **rest_document}},
            'auth': {
                'schema1': {
                    'tech': AuthTech.REST.value,
                    'url': url,
                    'method': method,
                    'options': {
                        'headers': headers,
                    },
                },
            },
        },
    )


def _graphql_fill(
    graphql_document: Dict,
    url: str,
    method: HTTPMethod,
    headers: Dict[str, str],
    variables: Optional[Dict] = None,
) -> RCFile:
    """This function fills the graphql escaperc file."""

    variables = variables or {}

    # Now we need to get the user information
    credentials: Dict = {}
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
                        credentials[argument['name']['value']][
                            input_object_field['name']['value']
                        ] = input_object_field['value']['value']

    rcfile = RCFile(
        {
            'users': {
                'user1': {
                    'auth': 'schema1',
                    **credentials,
                },
            },
            'auth': {
                'schema1': {
                    'tech': AuthTech.GRAPHQL.value,
                    'url': url,
                    'method': method,
                    'mutation_name': graphql_document['definitions'][0]['selection_set']['selections'][0]['name'][
                        'value'
                    ],
                    'options': {'operation': graphql_document['definitions'][0]['operation']},
                },
            },
        },
    )

    # Now regarding the field
    for field in graphql_document['definitions'][0]['selection_set']['selections'][0]['selection_set']['selections']:
        if field['name']['value'].lower() in POTENTIAL_FIELD_NAME:
            rcfile['auth']['schema1']['mutation_field'] = field['name']['value']
            break

    if headers:
        rcfile['auth']['schema1']['options']['headers'] = headers

    return rcfile


# pylint: disable=too-many-branches, too-many-statements
def curl_to_escaperc(curl: str) -> Optional[RCFile]:
    """This function transforms the curl request to an escaperc file."""

    # First we uncurl
    parsed_content = uncurl(curl)

    # First thing we have to check if in the headers, there is a basic authentication or a token already
    for header_prefix, header_value in parsed_content.headers.items():
        if 'authorization' in header_prefix.lower():
            if 'basic' in header_value.lower():
                LOGGER.info('Type of authetication detected: Basic')
                return _basic_fill(parsed_content.headers, header_value)
            # Here we assume it's manual headers.
            if parsed_content.data is None:
                LOGGER.info('Type of authetication detected: Manual Headers')
                return _manual_fill(parsed_content.headers)

    if parsed_content.data is not None:
        query: Optional[Dict] = None
        try:
            query = json.loads(parsed_content.data)
        except Exception:
            try:  # the request sent is not sent as application/json, let's try application/x-www-form-urlencoded
                json_data = urlencoded_to_json(parsed_content.data)
                if json_data is not None:
                    query = json.loads(json_data)
            except Exception:
                LOGGER.debug('The `data` attribute of the cURL is not JSONable')

        if query is not None:
            if query.get('query') is not None:
                LOGGER.info('Type of authetication detected: GraphQL')
                graphql_tree = graphql.parse(query['query']).to_dict()
                return _graphql_fill(
                    graphql_tree,
                    parsed_content.url,
                    parsed_content.method,
                    parsed_content.headers,
                    query.get('variables'),
                )

            LOGGER.info('Type of authetication detected: REST')
            return _rest_fill(query, parsed_content.url, parsed_content.method, parsed_content.headers)

    LOGGER.info('We could not determine any authentication method from the cURL.')
    return None
