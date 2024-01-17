import json
import re
from enum import StrEnum
from http import HTTPMethod
from typing import Any, Literal
from urllib.parse import parse_qs, urlparse

from pydantic import Field

from multiauth.lib.audit.events.base import (
    EventsList,
)
from multiauth.lib.audit.events.events import (
    ExtractedVariableEvent,
    HTTPFailureEvent,
    HTTPRequestEvent,
    HTTPResponseEvent,
)
from multiauth.lib.http_core.entities import (
    HTTPCookie,
    HTTPHeader,
    HTTPLocation,
    HTTPQueryParameter,
    HTTPRequest,
    HTTPResponse,
)
from multiauth.lib.http_core.mergers import merge_bodies, merge_cookies, merge_headers, merge_query_parameters
from multiauth.lib.http_core.parsers import parse_raw_url
from multiauth.lib.http_core.request import send_request
from multiauth.lib.runners.base import (
    BaseRunner,
    BaseRunnerConfiguration,
    BaseRunnerParameters,
    RunnerException,
    TokenExtraction,
)
from multiauth.lib.store.user import Credentials, User
from multiauth.lib.store.variables import AuthenticationVariable, interpolate_string

JSONSerializable = dict | list | str | int | float | bool


def extract_with_regex(string_list: list[str], regex_pattern: str | None) -> list[str]:
    if regex_pattern is None:
        return string_list  # Return an empty list when no regex is provided

    extracted_items = []
    for input_string in string_list:
        match = re.search(regex_pattern, input_string)
        if match:
            extracted_items.append(match.group())

    return extracted_items


def search_key_in_dict(body: dict, key: str) -> Any | None:
    """Search for a key in a dictionary."""

    if key in body:
        return body[key]

    for value in body.values():
        if isinstance(value, dict):
            result = search_key_in_dict(value, key)
            if result:
                return result

    return None


class HTTPScheme(StrEnum):
    HTTP = 'http'
    HTTPS = 'https'


class HTTPRequestParameters(BaseRunnerParameters):
    url: str = Field(description='The URL to send the request to')
    method: HTTPMethod = Field(
        default=HTTPMethod.POST,
        description='The HTTP method to use',
        examples=['GET', 'POST', 'PUT'],
    )
    headers: list[HTTPHeader] = Field(
        default_factory=list,
        description=(
            'The list of headers to attach to the request. Headers are merged with the user credentials headers. '
            'It is possible to attach mutliple values to a header.'
        ),
        examples=[
            HTTPHeader(name='Authorization', values=['Bearer my-token']),
            HTTPHeader(name='my-header', values=['value1', 'value2']),
        ],
    )
    cookies: list[HTTPCookie] = Field(
        default_factory=list,
        description=(
            'The list of cookies to attach to the request. Cookies are merged with the user credentials cookies. '
            'It is possible to attach mutliple values to a cookie. Cookie values are url-encoded before being sent.'
        ),
        examples=[
            HTTPCookie(name='PHPSESSIONID', values=['my-session-id']),
            HTTPCookie(name='my-cookie', values=['value1', 'value2']),
        ],
    )
    query_parameters: list[HTTPQueryParameter] = Field(
        default_factory=list,
        description=(
            'The list of query parameters to attach to the request. Query parameters are merged with the user '
            'credentials query parameters. It is possible to attach mutliple values to a query parameter. '
            'Query parameter values are url-encoded before being sent.'
        ),
        examples=[
            HTTPQueryParameter(name='token', values=['my-token']),
            HTTPQueryParameter(name='scope', values=['read-data', 'write-data']),
        ],
    )
    body: Any | None = Field(
        default=None,
        description=(
            'The body of the request. It can be a string or a JSON object. '
            'It is merged with the user credentials body if provided. If bodies of the HTTP request and of the user '
            'credentials are both JSON objects, they are merged. If the two bodies are strings, they are concatenated. '
            'If the two bodies are of different types, the body of the user credentials is used instead of this value.'
        ),
        examples=[
            'my body',
            {'key1': 'value1', 'key2': 'value2'},
            12345,
        ],
    )
    proxy: str | None = Field(
        default=None,
        description='An eventual proxy used for this request',
        examples=['http://my-proxy:8080'],
    )

    @staticmethod
    def examples() -> list:
        return [
            HTTPRequestParameters(
                url='https://my-api.com',
                method=HTTPMethod.GET,
            ).dict(exclude_defaults=True),
            HTTPRequestParameters(
                url='https://my-api.com',
                method=HTTPMethod.POST,
                headers=[HTTPHeader(name='Content-Type', values=['application/json'])],
                body={'key1': 'value1', 'key2': 'value2'},
            ).dict(exclude_defaults=True),
        ]


class HTTPRunnerConfiguration(BaseRunnerConfiguration):
    tech: Literal['http'] = 'http'
    extractions: list[TokenExtraction] = Field(
        default_factory=list,
        description=(
            'The list of extractions to run at the end of the operation.'
            'For HTTP operations, variables are extracted from the response.'
        ),
        examples=[
            *TokenExtraction.examples(),
        ],
    )
    parameters: HTTPRequestParameters = Field(
        description='The parameters of the HTTP request to send. At least a URL and a method must be provided.',
        examples=[
            HTTPRequestParameters(
                url='https://my-api.com',
                method=HTTPMethod.GET,
            ).dict(exclude_defaults=True),
            HTTPRequestParameters(
                url='https://my-api.com',
                method=HTTPMethod.POST,
                headers=[HTTPHeader(name='Content-Type', values=['application/json'])],
                body={'key1': 'value1', 'key2': 'value2'},
            ).dict(exclude_defaults=True),
        ],
    )

    def get_runner(self) -> 'HTTPRequestRunner':
        return HTTPRequestRunner(self)


class HTTPRequestRunner(BaseRunner[HTTPRunnerConfiguration]):
    def __init__(self, request_configuration: HTTPRunnerConfiguration):
        super().__init__(request_configuration)

    def interpolate(self, variables: list[AuthenticationVariable]) -> 'HTTPRequestRunner':
        request_configuration_str = self.request_configuration.model_dump_json()
        request_configuration_str = interpolate_string(request_configuration_str, variables)
        request_configuration = HTTPRunnerConfiguration.model_validate_json(request_configuration_str)

        return HTTPRequestRunner(request_configuration)

    def request(self, user: User) -> tuple[HTTPRequest, HTTPResponse | None, EventsList]:
        parameters = self.request_configuration.parameters

        events = EventsList()

        credentials = user.credentials or Credentials()

        scheme, host, path = parse_raw_url(parameters.url)
        headers = merge_headers(parameters.headers, credentials.headers)
        cookies = merge_cookies(parameters.cookies, credentials.cookies)
        query_parameters = merge_query_parameters(parameters.query_parameters, credentials.query_parameters)

        data = merge_bodies(parameters.body, credentials.body)
        data_text = None if data is None else data if isinstance(data, str) else json.dumps(data)
        data_json: Any = None
        try:
            data_json = None if data_text is None else json.loads(data_text)
        except json.JSONDecodeError:
            pass

        request = HTTPRequest(
            scheme=scheme,
            host=host,
            path=path,
            method=parameters.method,
            headers=headers,
            cookies=cookies,
            query_parameters=query_parameters,
            data_text=data_text,
            data_json=data_json,
            username=credentials.username,
            password=credentials.password,
            proxy=parameters.proxy,
        )

        events.append(HTTPRequestEvent(request=request))
        response = send_request(request)

        if isinstance(response, HTTPFailureEvent):
            events.append(response)
            return request, None, events

        events.append(HTTPResponseEvent(response=response))
        return request, response, events

    def extract(self, response: HTTPResponse | None) -> tuple[list[AuthenticationVariable], EventsList]:
        extractions = self.request_configuration.extractions

        events = EventsList()

        if response is None:
            return [], events

        variables: list[AuthenticationVariable] = []

        for extraction in extractions:
            match extraction.location:
                case HTTPLocation.HEADER:
                    h_findings = [h for h in response.headers if h.name == extraction.key]
                    if len(h_findings) == 0:
                        raise RunnerException(f'No header found with name {extraction.key}')
                    findings = extract_with_regex(h_findings[0].values, extraction.regex)
                    variable = AuthenticationVariable(name=extraction.slug, value=','.join(findings))
                    events.append(ExtractedVariableEvent(location=HTTPLocation.HEADER, variable=variable))
                    variables.append(variable)

                case HTTPLocation.COOKIE:
                    c_findings = [c for c in response.cookies if c.name == extraction.key]
                    if len(c_findings) == 0:
                        raise RunnerException(f'No cookie found with name {extraction.key}')
                    findings = extract_with_regex(c_findings[0].values, extraction.regex)
                    variable = AuthenticationVariable(name=extraction.slug, value=','.join(findings))
                    events.append(ExtractedVariableEvent(location=HTTPLocation.COOKIE, variable=variable))
                    variables.append(variable)

                case HTTPLocation.BODY:
                    if response.data_json is None:
                        continue
                    if not isinstance(response.data_json, dict):
                        continue
                    result = search_key_in_dict(response.data_json, extraction.key)
                    if result is None:
                        raise RunnerException(f'No body key found with name {extraction.key}')
                    result_str = str(result) if not isinstance(result, str) else result
                    findings = extract_with_regex([result_str], extraction.regex)
                    variable = AuthenticationVariable(name=extraction.slug, value=findings[0])
                    events.append(ExtractedVariableEvent(location=HTTPLocation.BODY, variable=variable))
                    variables.append(variable)

                case HTTPLocation.QUERY:
                    parsed_qp = parse_qs(urlparse(response.url).query)
                    q_finding = parsed_qp.get(extraction.key)
                    if q_finding is None:
                        raise RunnerException(f'No query parameter found with name {extraction.key}')
                    findings = extract_with_regex(q_finding, extraction.regex)
                    variable = AuthenticationVariable(name=extraction.slug, value=','.join(findings))
                    events.append(ExtractedVariableEvent(location=HTTPLocation.QUERY, variable=variable))
                    variables.append(variable)

        return variables, events

    def run(self, user: User) -> tuple[list[AuthenticationVariable], EventsList, RunnerException | None]:
        request, response, events = self.request(user)

        if response is None:
            return [], events, RunnerException('No response received.')

        if response.status_code >= 400:
            event = HTTPFailureEvent(reason='http_error', description=f'HTTP error {response.status_code}')
            events.append(event)
            return [], events, RunnerException(event.description)

        try:
            variables, extraction_events = self.extract(response)
        except RunnerException as e:
            return [], events, e
        events.extend(extraction_events)

        return variables, events, None
