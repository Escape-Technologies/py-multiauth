import json
from http import HTTPMethod
from typing import Any, Literal

from pydantic import Field

from multiauth.revamp.lib.http_core.entities import (
    HTTPCookie,
    HTTPHeader,
    HTTPLocation,
    HTTPQueryParameter,
    HTTPRequest,
    HTTPResponse,
)
from multiauth.revamp.lib.http_core.mergers import merge_bodies, merge_cookies, merge_headers, merge_query_parameters
from multiauth.revamp.lib.http_core.parsers import parse_raw_url
from multiauth.revamp.lib.http_core.request import send_request
from multiauth.revamp.lib.runners.base import (
    BaseExtraction,
    BaseRequestConfiguration,
    BaseRequestParameters,
    BaseRequestRunner,
)
from multiauth.revamp.lib.store.user import User
from multiauth.revamp.lib.store.variables import AuthenticationVariable, interpolate_string


class HTTPExtraction(BaseExtraction):
    name: str = Field(description='The name that will be used to store the extracted value')
    location: HTTPLocation = Field(description='The location where to search for the key')
    key: str = Field(
        description=(
            'The key to use to extract the value. Its usage depends on the location. For headers, cookies,'
            'and query parameters, this key describes the name of the header, cookie or query parameter. For a body '
            'location, the key is the field where the token should be injected within the request bodies'
        ),
    )


class HTTPRequestParameters(BaseRequestParameters):
    url: str
    method: HTTPMethod
    headers: list[HTTPHeader] = Field(default_factory=list)
    cookies: list[HTTPCookie] = Field(default_factory=list)
    query_parameters: list[HTTPQueryParameter] = Field(default_factory=list)
    body: Any | None = Field(default=None)


class HTTPRequestConfiguration(BaseRequestConfiguration):
    tech: Literal['http'] = 'http'
    extractions: list[HTTPExtraction] = Field(default_factory=list)
    parameters: HTTPRequestParameters

    def get_runner(self) -> 'HTTPRequestRunner':
        return HTTPRequestRunner(self)


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


class HTTPRequestRunner(BaseRequestRunner[HTTPRequestConfiguration]):
    def __init__(self, request_configuration: HTTPRequestConfiguration):
        self.request_configuration = request_configuration

    def interpolate(self, variables: list[AuthenticationVariable]) -> 'HTTPRequestRunner':
        request_configuration_str = self.request_configuration.model_dump_json()
        request_configuration_str = interpolate_string(request_configuration_str, variables)
        request_configuration = HTTPRequestConfiguration.model_validate_json(request_configuration_str)

        return HTTPRequestRunner(request_configuration)

    def request(self, user: User) -> tuple[HTTPRequest, HTTPResponse] | None:
        parameters = self.request_configuration.parameters

        scheme, host, path = parse_raw_url(parameters.url)
        headers = merge_headers(parameters.headers, user.credentials.headers)
        cookies = merge_cookies(parameters.cookies, user.credentials.cookies)
        query_parameters = merge_query_parameters(parameters.query_parameters, user.credentials.query_parameters)

        data = merge_bodies(parameters.body, user.credentials.body)
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
            username=user.credentials.username,
            password=user.credentials.password,
        )

        return request, send_request(request)

    def extract(self, response: HTTPResponse | None) -> list[AuthenticationVariable]:
        extractions = self.request_configuration.extractions

        if response is None:
            return []

        variables: list[AuthenticationVariable] = []

        for extraction in extractions:
            match extraction.location:
                case HTTPLocation.HEADER.value:
                    h_findings = [h for h in response.headers if h.name == extraction.key]
                    if len(h_findings) == 0:
                        continue
                    variables.append(AuthenticationVariable(name=extraction.name, value=','.join(h_findings[0].values)))
                case HTTPLocation.COOKIE.value:
                    c_findings = [c for c in response.cookies if c.name == extraction.key]
                    if len(c_findings) == 0:
                        continue
                    variables.append(AuthenticationVariable(name=extraction.name, value=','.join(h_findings[0].values)))
                case HTTPLocation.BODY.value:
                    if response.data_json is None:
                        continue
                    if not isinstance(response.data_json, dict):
                        continue
                    result = search_key_in_dict(response.data_json, extraction.key)
                    if result is None:
                        continue
                    result_str = str(result) if not isinstance(result, str) else result
                    variables.append(AuthenticationVariable(name=extraction.name, value=result_str))

        return variables
