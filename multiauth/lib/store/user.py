from typing import Any, Literal

from pydantic import Field

from multiauth.helpers.base_model import StrictBaseModel
from multiauth.lib.entities import ProcedureName, UserName
from multiauth.lib.http_core.entities import (
    HTTPCookie,
    HTTPHeader,
    HTTPQueryParameter,
)
from multiauth.lib.store.variables import AuthenticationVariable


class Credentials(StrictBaseModel):
    username: UserName | None = Field(
        default=None,
        description='The username to attach to the HTTP requests sent for this user. See https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url',
        examples=['john'],
    )
    password: str | None = Field(
        default=None,
        description='The password to attach to the HTTP requests sent for this user. See https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url',
        examples=['john@password123#'],
    )
    headers: list[HTTPHeader] = Field(
        default_factory=list,
        description='A list of headers to attach to every HTTP requests sent for this user',
        examples=[
            HTTPHeader(
                name='Authorization',
                values=['Bearer ...'],
            ),
        ],
    )
    cookies: list[HTTPCookie] = Field(
        default_factory=list,
        description='A list of cookies to attach to every HTTP requests sent for this user',
        examples=[
            HTTPCookie(
                name='PHPSESSIONID',
                values=['...'],
            ),
        ],
    )
    query_parameters: list[HTTPQueryParameter] = Field(
        default_factory=list,
        serialization_alias='queryParameters',
        description='A list of query parameters to attach to every HTTP requests sent for this user',
        examples=[
            HTTPQueryParameter(
                name='token',
                values=['...'],
            ),
        ],
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

    @staticmethod
    def from_credentials(credentials: 'Credentials') -> 'Credentials':
        return Credentials(
            username=credentials.username,
            password=credentials.password,
            headers=credentials.headers,
            cookies=credentials.cookies,
            body=credentials.body,
        )


InvalidSessionDetectionStrategy = Literal['status_code']


class UserRefresh(StrictBaseModel):
    procedure: ProcedureName | None = Field(
        default=None,
        description=(
            'An optional custom procedure to use to refresh the authentication of the user. '
            'Defaults to the user procedure if not provided. '
            'This name MUST match the `name` field of a procedure in the `procedures` list in the '
            'multiauth configuration.'
        ),
    )
    session_seconds: int | None = Field(
        default=None,
        serialization_alias='sessionSeconds',
        description=(
            'Number of seconds to wait before refreshing the authentication. If not provided, multiauth will'
            'try to infer the session duration from the returned variables'
        ),
    )
    keep: bool = Field(
        default=False,
        description=(
            'If true, multiauth will keep the current tokens and use a merge of the refreshed authentication'
            'and the current one.'
        ),
    )
    credentials: Credentials | None = Field(
        default=None,
        description=(
            'Credentials to use to refresh the authentication. If not provided, the user credentials will be used.'
        ),
    )
    variables: list[AuthenticationVariable] | None = Field(
        default=None,
        description=(
            "List of variables that will be injected at the beginning of the user's"
            "refresh procedure. If not provided, the user's variables will be used instead."
        ),
    )


class User(StrictBaseModel):
    name: UserName = Field(description='The name of the user')
    credentials: Credentials | None = Field(
        description='A set of HTTP parameters used to customize requests sent for the user.',
        default=None,
    )
    procedure: ProcedureName | None = Field(
        description=(
            'The name of the procedure to use to authenticate the user.'
            'This name MUST match the `name` field of a procedure in the `procedures` list in the '
            'multiauth configuration.'
        ),
        default=None,
    )
    variables: list[AuthenticationVariable] = Field(
        default_factory=list,
        description="List of variables that will be injected at the beginning of the user's authentication procedure.",
    )
    refresh: UserRefresh | None = Field(
        default=None,
        description='An optional refresh procedure to follow for the user.',
    )

    @property
    def session_ttl_seconds(self) -> int | None:
        ttl_seconds = None

        # In case of a user-provided ttl for this user, use it instead of any ttl declared before
        if self.refresh is not None:
            ttl_seconds = self.refresh.session_seconds

        return ttl_seconds

    @property
    def refresh_variables(self) -> list[AuthenticationVariable]:
        if self.refresh is None:
            return self.variables
        return self.refresh.variables or self.variables

    @property
    def refresh_credentials(self) -> Credentials | None:
        if self.refresh is None:
            return self.credentials
        return self.refresh.credentials or self.credentials

    @property
    def refresh_user(self) -> 'User':
        refresh_user = User.from_user(self)

        if self.refresh is not None:
            refresh_user.variables = self.refresh_variables or self.variables
            refresh_user.credentials = self.refresh_credentials or self.credentials
            refresh_user.procedure = self.refresh.procedure or self.procedure

        return refresh_user

    @staticmethod
    def from_user(user: 'User') -> 'User':
        return User(
            name=user.name,
            credentials=Credentials.from_credentials(user.credentials or Credentials()),
            procedure=user.procedure,
            variables=user.variables,
            refresh=user.refresh,
        )

    @staticmethod
    def public() -> 'User':
        return User(
            name=UserName('public'),
            credentials=Credentials(),
            procedure=None,
            variables=[],
            refresh=None,
        )
