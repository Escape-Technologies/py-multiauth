import json
from http import HTTPMethod
from typing import Annotated, Any, Literal, Union

import requests
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
    HTTPQueryParameter,
    HTTPRequest,
    HTTPResponse,
)
from multiauth.lib.http_core.mergers import merge_bodies, merge_cookies, merge_headers, merge_query_parameters
from multiauth.lib.http_core.parsers import parse_raw_url
from multiauth.lib.http_core.request import send_request
from multiauth.lib.runners.base import (
    BaseExtraction,
    BaseRunner,
    BaseRunnerConfiguration,
    BaseRunnerParameters,
    RunnerException,
)
from multiauth.lib.store.user import User
from multiauth.lib.store.variables import AuthenticationVariable, interpolate_string


class HTTPHeaderExtraction(BaseExtraction):
    location: Literal['header'] = 'header'
    key: str = Field(description=('The name of the header to extract the value from'))


class HTTPCookieExtraction(BaseExtraction):
    location: Literal['cookie'] = 'cookie'
    key: str = Field(description=('The name of the cookie to extract the value from'))


class HTTPBodyExtraction(BaseExtraction):
    location: Literal['body'] = 'body'
    key: str = Field(description='The key to extract the value from the body. The key is searched recursively.')


HTTPExtractionType = Annotated[
    Union[HTTPHeaderExtraction, HTTPCookieExtraction, HTTPBodyExtraction],
    Field(discriminator='location'),
]


class HTTPRequestParameters(BaseRunnerParameters):
    url: str
    method: HTTPMethod
    headers: list[HTTPHeader] = Field(default_factory=list)
    cookies: list[HTTPCookie] = Field(default_factory=list)
    query_parameters: list[HTTPQueryParameter] = Field(default_factory=list)
    body: Any | None = Field(default=None)
    proxy: str | None = Field(default=None)


class HTTPRunnerConfiguration(BaseRunnerConfiguration):
    tech: Literal['http'] = 'http'
    extractions: list[HTTPExtractionType] = Field(default_factory=list)
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
            proxy=parameters.proxy,
        )

        events.append(HTTPRequestEvent(request=request))
        response = None
        try:
            response = send_request(request)
            events.append(HTTPResponseEvent(response=response))
        except requests.exceptions.Timeout as e:
            events.append(HTTPFailureEvent(reason='timeout', description=str(e)))
        except requests.exceptions.ConnectionError as e:
            events.append(HTTPFailureEvent(reason='connection_error', description=str(e)))
        except requests.exceptions.TooManyRedirects as e:
            events.append(HTTPFailureEvent(reason='too_many_redirects', description=str(e)))
        except Exception as e:
            events.append(HTTPFailureEvent(reason='unknown', description=str(e)))

        return request, response, events

    def extract(self, response: HTTPResponse | None) -> tuple[list[AuthenticationVariable], EventsList]:
        extractions = self.request_configuration.extractions

        events = EventsList()

        if response is None:
            return [], events

        variables: list[AuthenticationVariable] = []

        for extraction in extractions:
            if isinstance(extraction, HTTPHeaderExtraction):
                h_findings = [h for h in response.headers if h.name == extraction]
                if len(h_findings) == 0:
                    continue
                variable = AuthenticationVariable(name=extraction.name, value=','.join(h_findings[0].values))
                events.append(ExtractedVariableEvent(variable=variable))
                variables.append(variable)

            if isinstance(extraction, HTTPCookieExtraction):
                c_findings = [c for c in response.cookies if c.name == extraction.key]
                if len(c_findings) == 0:
                    continue
                variable = AuthenticationVariable(name=extraction.name, value=','.join(h_findings[0].values))
                events.append(ExtractedVariableEvent(variable=variable))
                variables.append(variable)

            if isinstance(extraction, HTTPBodyExtraction):
                if response.data_json is None:
                    continue
                if not isinstance(response.data_json, dict):
                    continue
                result = search_key_in_dict(response.data_json, extraction.key)
                if result is None:
                    continue
                result_str = str(result) if not isinstance(result, str) else result
                variable = AuthenticationVariable(name=extraction.name, value=result_str)
                events.append(ExtractedVariableEvent(variable=variable))
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

        variables, extraction_events = self.extract(response)
        events.extend(extraction_events)

        return variables, events, None
