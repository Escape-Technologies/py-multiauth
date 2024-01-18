from http import HTTPMethod
from typing import Any, Literal, Sequence

from pydantic import BaseModel, Field

from multiauth.lib.entities import ProcedureName, UserName, VariableName
from multiauth.lib.http_core.entities import HTTPCookie, HTTPHeader, HTTPLocation, HTTPQueryParameter
from multiauth.lib.injection import TokenInjection
from multiauth.lib.presets.base import BasePreset, BasePresetDoc, BaseUserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import HTTPRequestParameters, HTTPRunnerConfiguration, TokenExtraction
from multiauth.lib.store.user import Credentials, User

VARIABLE_NAME = VariableName('token')


def to_headers(headers: dict[str, str] | None) -> list[HTTPHeader]:
    if headers is None:
        return []
    return [HTTPHeader(name=k, values=[v]) for k, v in headers.items()]


def to_cookies(cookies: dict[str, str] | None) -> list[HTTPCookie]:
    if cookies is None:
        return []
    return [HTTPCookie(name=k, values=[v]) for k, v in cookies.items()]


def to_query_parameters(query_parameters: dict[str, str] | None) -> list[HTTPQueryParameter]:
    if query_parameters is None:
        return []
    return [HTTPQueryParameter(name=k, values=[v]) for k, v in query_parameters.items()]


class HTTPUserPreset(BaseUserPreset):
    username: UserName = Field(
        default=None,
        description='The username to attach to the HTTP requests sent for this user. See https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url',
        examples=['john'],
    )
    password: str | None = Field(
        default=None,
        description='The password to attach to the HTTP requests sent for this user. See https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url',
        examples=['john@password123#'],
    )
    headers: dict[str, str] | None = Field(
        default_factory=dict,
        description='A dict representing the headers to attach to every HTTP requests sent for this user',
        examples=[{'Authorization': 'Bearer ...'}],
    )
    cookies: dict[str, str] | None = Field(
        default_factory=dict,
        description='A dict representing the cookies to attach to every HTTP requests sent for this user',
        examples=[{'PHPSESSIONID': '...'}],
    )
    query_parameters: dict[str, str] | None = Field(
        default_factory=dict,
        serialization_alias='queryParameters',
        description='A dict of query parameters to attach to every HTTP requests sent for this user',
        examples=[{'sessionId': '...'}],
    )
    body: Any | None = Field(
        default=None,
        description='A body to merge with the bodies of every HTTP requests sent for this user',
        examples=[
            {
                'username': 'john',
                'password': 'john@password123#',
            },
            'username=john&password=john%40password123%23',
        ],
    )


class HTTPRequestPreset(BaseModel):
    url: str = Field(description='The URL to send the request to')
    method: HTTPMethod = Field(
        default=HTTPMethod.POST,
        description='The HTTP method to use',
        examples=['GET', 'POST', 'PUT'],
    )
    headers: dict[str, str] | None = Field(
        default_factory=dict,
        description=(
            'The list of headers to attach to the request. Headers are merged with the user credentials headers. '
            'It is possible to attach mutliple values to a header.'
        ),
        examples=[{'Authorization': 'Bearer my-global-token', 'my-header': 'global-value'}],
    )
    cookies: dict[str, str] | None = Field(
        default_factory=dict,
        description=(
            'The list of cookies to attach to the request. Cookies are merged with the user credentials cookies. '
            'It is possible to attach mutliple values to a cookie. Cookie values are url-encoded before being sent.'
        ),
        examples=[{'PHPSESSIONID': 'my-global-php-session-id'}],
    )
    query_parameters: dict[str, str] | None = Field(
        default_factory=dict,
        description=(
            'The list of query parameters to attach to the request. Query parameters are merged with the user '
            'credentials query parameters. It is possible to attach mutliple values to a query parameter. '
            'Query parameter values are url-encoded before being sent.'
        ),
        examples=[{'sessionId': 'my-global-session-id'}],
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

    def to_std_http_parameters(self) -> HTTPRequestParameters:
        return HTTPRequestParameters(
            url=self.url,
            method=self.method,
            headers=to_headers(self.headers),
            cookies=to_cookies(self.cookies),
            body=self.body,
            query_parameters=to_query_parameters(self.query_parameters),
            proxy=None,
        )


class HTTPPreset(BasePreset):
    type: Literal['http'] = 'http'
    request: HTTPRequestPreset = Field(
        description=('The parameters of the HTTP request used to fetch the access and refresh tokens.'),
    )
    extract: TokenExtraction = Field(
        description='The token extraction configuration used to extract the tokens from the HTTP response.',
        examples=TokenExtraction.examples(),
    )
    inject: TokenInjection = Field(
        description='The injection configuration used to inject the tokens into the HTTP requests.',
        examples=TokenInjection.examples(),
    )

    users: Sequence[HTTPUserPreset] = Field(
        description='The list of users to generate tokens for.',
    )

    @staticmethod
    def _doc() -> BasePresetDoc:
        return BasePresetDoc(
            title='HTTP',
            description="""The 'HTTP' authentication preset is designed to handle authentication via structured HTTP requests:

- **Structured Request**: Authentication is performed through a well-defined HTTP request, including URL, method, headers, cookies, query parameters, and body.
- **Dynamic Token Management**: The preset handles the extraction of authentication tokens from the HTTP response and subsequently reinjects them into future requests.
- **User Credentials**: Supports attaching various credentials to each user, such as username, password, headers, cookies, and other request parameters.

This method is particularly effective in scenarios where authentication is managed via custom HTTP endpoints, requiring precise control over request composition and token handling.""",  # noqa: E501
            examples=[
                HTTPPreset(
                    type='http',
                    request=HTTPRequestPreset(
                        url='https://api.example.com/authenticate',
                        method=HTTPMethod.POST,
                        headers={'Content-Type': 'application/json'},
                        body={'addtional': 'body', 'for': 'authentication'},
                    ),
                    extract=TokenExtraction(
                        location=HTTPLocation.BODY,
                        key='accessToken',
                    ),
                    inject=TokenInjection(
                        location=HTTPLocation.HEADER,
                        key='Authorization',
                        prefix='Bearer ',
                    ),
                    users=[
                        HTTPUserPreset(
                            username=UserName('user1'),
                            body={
                                'login': 'user1',
                                'password': 'pass1',
                            },
                        ),
                        HTTPUserPreset(
                            username=UserName('user2'),
                            headers={'addtional': 'header'},
                            cookies={'addtional': 'cookie'},
                            query_parameters={'addtional': 'query param'},
                            body={
                                'login': 'user2',
                                'password': 'pass2',
                            },
                        ),
                    ],
                ),
            ],
        )

    def to_procedure_configurations(self) -> list[ProcedureConfiguration]:
        return [
            ProcedureConfiguration(
                name=ProcedureName(self.slug),
                injections=[
                    TokenInjection(
                        location=self.inject.location,
                        key=self.inject.key,
                        prefix=self.inject.prefix,
                        variable=VariableName(VARIABLE_NAME),
                    ),
                ],
                operations=[
                    HTTPRunnerConfiguration(
                        parameters=self.request.to_std_http_parameters(),
                        extractions=[
                            TokenExtraction(
                                location=self.extract.location,
                                name=VariableName(VARIABLE_NAME),
                                key=self.extract.key,
                                regex=self.extract.regex,
                            ),
                        ],
                    ),
                ],
            ),
        ]

    def to_users(self) -> list[User]:
        return [
            User(
                name=user.username,
                credentials=Credentials(
                    username=user.username,
                    password=user.password,
                    headers=to_headers(user.headers),
                    cookies=to_cookies(user.cookies),
                    body=user.body,
                    query_parameters=to_query_parameters(user.query_parameters),
                ),
                procedure=self.slug,
            )
            for user in self.users
        ]
