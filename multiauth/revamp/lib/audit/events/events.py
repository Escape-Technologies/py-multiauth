from typing import Literal

from multiauth.revamp.lib.audit.events.base import Event
from multiauth.revamp.lib.http_core.entities import HTTPLocation, HTTPRequest, HTTPResponse
from multiauth.revamp.lib.store.variables import AuthenticationVariable


class HTTPRequestEvent(Event):
    type: Literal['http_request'] = 'http_request'
    default_severity: Literal['info'] = 'info'
    request: HTTPRequest


class HTTPFailureEvent(Event):
    type: Literal['http_failure'] = 'http_failure'
    default_severity: Literal['error'] = 'error'
    reason: Literal['timeout', 'connection_error', 'too_many_redirects', 'unknown']
    description: str


class ProcedureStartedEvent(Event):
    type: Literal['procedure_started'] = 'procedure_started'
    default_severity: Literal['info'] = 'info'
    procedure_name: str
    user_name: str


class ProcedureAbortedEvent(Event):
    type: Literal['procedure_aborted'] = 'procedure_aborted'
    default_severity: Literal['error'] = 'error'
    reason: Literal['http_error', 'unknown']
    description: str


class HTTPResponseEvent(Event):
    type: Literal['http_response'] = 'http_response'
    default_severity: Literal['success'] = 'success'
    response: HTTPResponse


class ExtractedVariableEvent(Event):
    type: Literal['extraction'] = 'extraction'
    default_severity: Literal['info'] = 'info'
    variable: AuthenticationVariable


class InjectedVariableEvent(Event):
    type: Literal['injection'] = 'injection'
    default_severity: Literal['info'] = 'info'
    location: HTTPLocation
    target: str
    variable: AuthenticationVariable
    # authentication: Authentication


class ProcedureEndedEvent(Event):
    type: Literal['procedure_finished'] = 'procedure_finished'
    default_severity: Literal['info'] = 'info'
    user_name: str
    # authentication: Authentication
