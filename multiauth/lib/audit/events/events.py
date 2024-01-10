from typing import Literal

from multiauth.lib.audit.events.base import Event
from multiauth.lib.http_core.entities import HTTPLocation, HTTPRequest, HTTPResponse
from multiauth.lib.store.variables import AuthenticationVariable


class HTTPRequestEvent(Event):
    type: Literal['http_request'] = 'http_request'
    default_severity: Literal['info'] = 'info'
    request: HTTPRequest

    @property
    def logline(self) -> str:
        txt = f' {self.request.method} {self.request.scheme}://{self.request.host}{self.request.path}\n'
        for header in self.request.headers:
            for v in header.values:
                txt += f'H> {header.name}: {v}\n'
        for cookie in self.request.cookies:
            for v in cookie.values:
                txt += f'C> {cookie.name}: {v}\n'
        txt += f'{self.request.data_text}'

        return txt


class HTTPFailureEvent(Event):
    type: Literal['http_failure'] = 'http_failure'
    default_severity: Literal['error'] = 'error'
    reason: Literal['timeout', 'connection_error', 'too_many_redirects', 'unknown', 'http_error']
    description: str

    @property
    def logline(self) -> str:
        return f'{self.reason} {self.description}'


class HTTPResponseEvent(Event):
    type: Literal['http_response'] = 'http_response'
    default_severity: Literal['success'] = 'success'
    response: HTTPResponse

    @property
    def logline(self) -> str:
        txt = f' {self.response.status_code} {self.response.reason} in {self.response.elapsed.microseconds//1000}ms\n'
        for header in self.response.headers:
            for v in header.values:
                txt += f'H< {header.name}: {v}\n'
        for cookie in self.response.cookies:
            for v in cookie.values:
                txt += f'C< {cookie.name}: {v}\n'
        txt += f'{self.response.data_text}'

        return txt


class SeleniumScriptLogEvent(Event):
    type: Literal['selenium_log'] = 'selenium_log'
    default_severity: Literal['info'] = 'info'
    message: str

    @property
    def logline(self) -> str:
        return self.message


class SeleniumScriptErrorEvent(Event):
    type: Literal['selenium_error'] = 'selenium_error'
    default_severity: Literal['error'] = 'error'
    message: str
    from_exception: str | None = None

    @property
    def logline(self) -> str:
        return f'{self.message}: {self.from_exception}'


class ProcedureStartedEvent(Event):
    type: Literal['procedure_started'] = 'procedure_started'
    default_severity: Literal['info'] = 'info'
    procedure_name: str
    user_name: str

    @property
    def logline(self) -> str:
        return f'{self.procedure_name} started for user {self.user_name}'


class ProcedureAbortedEvent(Event):
    type: Literal['procedure_aborted'] = 'procedure_aborted'
    default_severity: Literal['error'] = 'error'
    reason: Literal['runner_error', 'unknown']
    description: str

    @property
    def logline(self) -> str:
        return f'{self.reason} {self.description}'


class ExtractedVariableEvent(Event):
    type: Literal['extraction'] = 'extraction'
    default_severity: Literal['info'] = 'info'
    variable: AuthenticationVariable

    @property
    def logline(self) -> str:
        return f'{self.variable.name}={self.variable.value}'


class InjectedVariableEvent(Event):
    type: Literal['injection'] = 'injection'
    default_severity: Literal['info'] = 'info'
    location: HTTPLocation
    target: str
    variable: AuthenticationVariable

    @property
    def logline(self) -> str:
        return f'{self.variable.value} in {self.location} {self.target}'


class ProcedureSkippedEvent(Event):
    type: Literal['procedure_skipped'] = 'procedure_skipped'
    default_severity: Literal['info'] = 'info'
    user_name: str

    @property
    def logline(self) -> str:
        return f'Procedures skipped for user {self.user_name}'


class ProcedureEndedEvent(Event):
    type: Literal['procedure_finished'] = 'procedure_finished'
    default_severity: Literal['info'] = 'info'
    user_name: str

    @property
    def logline(self) -> str:
        return f'procedure ended for user {self.user_name}'
