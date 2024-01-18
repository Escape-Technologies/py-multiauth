import hashlib
from http import HTTPMethod
from typing import Literal

from pydantic import Field

from multiauth.helpers.base_model import StrictBaseModel
from multiauth.lib.audit.events.base import EventsList
from multiauth.lib.audit.events.events import HTTPFailureEvent
from multiauth.lib.http_core.entities import HTTPHeader, HTTPLocation
from multiauth.lib.http_core.mergers import merge_headers
from multiauth.lib.runners.base import BaseRunnerConfiguration, RunnerException
from multiauth.lib.runners.http import (
    HTTPRequestParameters,
    HTTPRequestRunner,
    HTTPRunnerConfiguration,
    TokenExtraction,
)
from multiauth.lib.store.user import Credentials, User
from multiauth.lib.store.variables import AuthenticationVariable, VariableName, interpolate_string


class DigestSecondRequestConfiguration(StrictBaseModel):
    url: str | None = Field(
        default=None,
        description=(
            'The URL of the second HTTP request executed during the digest procedure.'
            'By default, the URL of the first request is used.'
        ),
    )
    method: HTTPMethod | None = Field(
        default=None,
        description=(
            'The method of the second HTTP request executed during the digest procedure.'
            'By default, the method of the first request is used.'
        ),
        examples=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD', 'TRACE', 'CONNECT'],
    )

    @staticmethod
    def examples() -> list:
        return [
            DigestSecondRequestConfiguration(
                url='https://auth.example.com/digest',
                method=HTTPMethod.POST,
            ).dict(exclude_defaults=True),
        ]


class DigestRequestSequenceConfiguration(StrictBaseModel):
    first_request: HTTPRequestParameters = Field(
        description=(
            'The parameters of the first HTTP request executed during the digest procedure.'
            'It is the one that returns the WWW-Authenticate header.'
        ),
        examples=HTTPRequestParameters.examples(),
    )
    second_request: DigestSecondRequestConfiguration | None = Field(
        default=None,
        description=(
            'The parameters of the second HTTP request executed during the digest procedure.'
            'It is the one that uses the digest authentication. By default, parameters of the first request are used.'
        ),
        examples=DigestSecondRequestConfiguration.examples(),
    )

    @staticmethod
    def examples() -> list:
        return [
            DigestRequestSequenceConfiguration(
                first_request=HTTPRequestParameters(
                    url='https://example.com',
                    method=HTTPMethod.GET,
                    headers=[HTTPHeader(name='Accept', values=['*/*'])],
                ),
                second_request=None,
            ).dict(exclude_defaults=True),
            DigestRequestSequenceConfiguration(
                first_request=HTTPRequestParameters(
                    url='https://example.com',
                    method=HTTPMethod.GET,
                    headers=[HTTPHeader(name='Accept', values=['*/*'])],
                ),
                second_request=DigestSecondRequestConfiguration(
                    url='/digest',
                    method=HTTPMethod.GET,
                ),
            ).dict(exclude_defaults=True),
        ]


class DigestRunnerConfiguration(BaseRunnerConfiguration):
    tech: Literal['digest'] = 'digest'
    parameters: DigestRequestSequenceConfiguration = Field(
        description=(
            'The parameters of the HTTP requests executed during the digest procedure.'
            'It features two HTTP requests: the first one is the one that returns the WWW-Authenticate header,'
            'and the second one is the one that uses the digest authentication.'
        ),
        examples=DigestRequestSequenceConfiguration.examples(),
    )

    def to_http(self) -> HTTPRunnerConfiguration:
        return HTTPRunnerConfiguration(
            extractions=[],
            parameters=self.parameters.first_request,
        )

    def get_runner(self) -> 'DigestRunner':
        return DigestRunner(self)

    @staticmethod
    def examples() -> list:
        return [
            DigestRunnerConfiguration(
                parameters=DigestRequestSequenceConfiguration(
                    first_request=HTTPRequestParameters(
                        url='https://example.com',
                        method=HTTPMethod.GET,
                        headers=[HTTPHeader(name='Accept', values=['*/*'])],
                    ),
                    second_request=None,
                ),
                extractions=[],
            ).dict(exclude_defaults=True),
            DigestRunnerConfiguration(
                parameters=DigestRequestSequenceConfiguration(
                    first_request=HTTPRequestParameters(
                        url='https://example.com',
                        method=HTTPMethod.GET,
                        headers=[HTTPHeader(name='Accept', values=['*/*'])],
                    ),
                    second_request=DigestSecondRequestConfiguration(
                        url='/digest',
                        method=HTTPMethod.GET,
                    ),
                ),
                extractions=[
                    TokenExtraction(
                        name=VariableName('digest-header-value'),
                        location=HTTPLocation.HEADER,
                        key='Authorization',
                    ),
                ],
            ).dict(exclude_defaults=True),
        ]


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


class DigestServerParameters(StrictBaseModel):
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
        events = EventsList()
        variables: list[AuthenticationVariable] = []

        credentials = user.credentials or Credentials()

        if not credentials.username or not credentials.password:
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
            username=credentials.username,
            password=credentials.password,
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
            if self.digest_configuration.parameters.second_request.url is not None:
                second_request_path = self.digest_configuration.parameters.second_request.url
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
