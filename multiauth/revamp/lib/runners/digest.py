import hashlib
from http import HTTPMethod
from typing import Literal

from pydantic import BaseModel

from multiauth.revamp.lib.audit.events.base import EventsList
from multiauth.revamp.lib.audit.events.events import HTTPFailureEvent
from multiauth.revamp.lib.http_core.entities import HTTPHeader
from multiauth.revamp.lib.http_core.mergers import merge_headers
from multiauth.revamp.lib.runners.base import BaseRunnerConfiguration, RunnerException
from multiauth.revamp.lib.runners.http import HTTPRequestParameters, HTTPRequestRunner, HTTPRunnerConfiguration
from multiauth.revamp.lib.store.user import User
from multiauth.revamp.lib.store.variables import AuthenticationVariable, VariableName, interpolate_string


class DigestSecondRequestConfiguration(BaseModel):
    path: str | None = None
    method: HTTPMethod | None = None


class DigestRequestSequenceConfiguration(BaseModel):
    first_request: HTTPRequestParameters
    second_request: DigestSecondRequestConfiguration | None = None


class DigestRunnerConfiguration(BaseRunnerConfiguration):
    tech: Literal['digest'] = 'digest'
    parameters: DigestRequestSequenceConfiguration

    def to_http(self) -> HTTPRunnerConfiguration:
        return HTTPRunnerConfiguration(
            extractions=[],
            parameters=self.parameters.first_request,
        )

    def get_runner(self) -> 'DigestRunner':
        return DigestRunner(self)


def build_digest_headers(realm: str, username: str, password: str, domain: str, method: str, nonce: str) -> HTTPHeader:
    if not domain.endswith('/'):
        domain = domain + '/'

    ha1_text = f'{username}:{realm}:{password}'
    #     method = request.method
    ha2_text = f'{method}:{domain}'
    HA1 = hashlib.md5(ha1_text.encode()).hexdigest()  # noqa: S324
    HA2 = hashlib.md5(ha2_text.encode()).hexdigest()  # noqa: S324

    value = (
        f'Digest username={username}'
        f' realm={realm}'
        f' nonce={nonce}'
        f' uri={domain}'
        f' response={hashlib.md5(f"{HA1}:{nonce}:{HA2}".encode()).hexdigest()}'  # noqa: S324
    )

    return HTTPHeader(name='Authorization', values=[value])


class DigestServerParameters(BaseModel):
    realm: str
    nonce: str
    qop: str | None = None
    opaque: str | None = None


class DigestRunner(HTTPRequestRunner):
    digest_configuration: DigestRunnerConfiguration

    def __init__(self, configuration: DigestRunnerConfiguration) -> None:
        self.digest_configuration = configuration
        super().__init__(self.digest_configuration.to_http())

    def interpolate(self, variables: list[AuthenticationVariable]) -> 'DigestRunner':
        digest_configuration_str = self.digest_configuration.model_dump_json()
        digest_configuration_str = interpolate_string(digest_configuration_str, variables)
        digest_configuration = DigestRunnerConfiguration.model_validate_json(digest_configuration_str)

        return DigestRunner(digest_configuration)

    def run(self, user: User) -> tuple[list[AuthenticationVariable], EventsList, RunnerException | None]:
        events: EventsList = []
        variables: list[AuthenticationVariable] = []

        if not user.credentials.username or not user.credentials.password:
            raise ValueError(f'User {user.name} is missing a username or password.')

        request, response, http_events = super().request(user)
        events.extend(http_events)

        if response is None:
            return [], events, RunnerException('No response received.')

        www_authenticate_header = next(
            (header for header in response.headers if header.name.lower() == 'www-authenticate'),
            None,
        )

        if www_authenticate_header is None:
            event = HTTPFailureEvent(reason='http_error', description='Digest response has no WWW-Authenticate header.')
            events.append(event)
            return [], events, RunnerException(event.description)

        raw_headers = www_authenticate_header.values

        realm: str | None = None
        nonce: str | None = None
        qop: str | None = None
        opaque: str | None = None
        domain: str | None = None

        for raw_header in raw_headers:
            splitted = raw_header.split(' ')
            if len(splitted) != 2:
                continue

            splitted = splitted[1].split('=')
            if len(splitted) != 2:
                continue

            key, value = splitted

            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]

            match key.lower():
                case 'realm':
                    realm = value
                case 'domain':
                    domain = value
                case 'nonce':
                    nonce = value
                case 'qop':
                    qop = value
                case 'opaque':
                    opaque = value
                case _:
                    pass

        if realm is None or nonce is None:
            event = HTTPFailureEvent(
                reason='http_error',
                description='Digest response has no realm or nonce.',
            )
            events.append(event)
            return [], events, RunnerException(event.description)

        if domain is None:
            domain = request.path

        header = build_digest_headers(
            realm=realm,
            username=user.credentials.username,
            password=user.credentials.password,
            domain=domain,
            method=request.method,
            nonce=nonce,
        )

        variables.append(AuthenticationVariable(name=VariableName('realm'), value=realm))
        variables.append(AuthenticationVariable(name=VariableName('nonce'), value=nonce))
        if qop is not None:
            variables.append(AuthenticationVariable(name=VariableName('qop'), value=qop))
        if opaque is not None:
            variables.append(AuthenticationVariable(name=VariableName('opaque'), value=opaque))
        variables.append(AuthenticationVariable(name=VariableName('domain'), value=domain))
        variables.append(AuthenticationVariable(name=VariableName('digest-header-value'), value=header.values[0]))

        request_parameters = self.digest_configuration.parameters.first_request
        second_request_path = domain

        if self.digest_configuration.parameters.second_request is not None:
            if self.digest_configuration.parameters.second_request.path is not None:
                second_request_path = self.digest_configuration.parameters.second_request.path
            if self.digest_configuration.parameters.second_request.method is not None:
                request_parameters.method = self.digest_configuration.parameters.second_request.method

        next_request_config = HTTPRunnerConfiguration(
            extractions=self.request_configuration.extractions,
            parameters=HTTPRequestParameters(
                url=request.host + second_request_path,
                method=request_parameters.method,
                headers=merge_headers(request_parameters.headers, [header]),
                cookies=request_parameters.cookies,
                proxy=request_parameters.proxy,
                query_parameters=request_parameters.query_parameters,
            ),
        )

        next_variables, next_events, exception = HTTPRequestRunner(next_request_config).run(user)
        events.extend(next_events)
        variables.extend(next_variables)

        return variables, events, exception
