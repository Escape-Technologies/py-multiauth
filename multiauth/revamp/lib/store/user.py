from typing import Any, Literal

from pydantic import BaseModel, Field

from multiauth.revamp.lib.http_core.entities import (
    HTTPCookie,
    HTTPHeader,
    HTTPQueryParameter,
)
from multiauth.revamp.lib.store.injection import TokenInjection


class Credentials(BaseModel):
    username: str | None = Field(
        default=None,
        description='The username to attach to the HTTP requests sent for this user. See https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url',
    )
    password: str | None = Field(
        default=None,
        description='The password to attach to the HTTP requests sent for this user. See https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#access_using_credentials_in_the_url',
    )
    headers: list[HTTPHeader] = Field(
        default_factory=list,
        description='A list of headers to attach to every HTTP requests sent for this user',
    )
    cookies: list[HTTPCookie] = Field(
        default_factory=list,
        description='A list of cookies to attach to every HTTP requests sent for this user',
    )
    query_parameters: list[HTTPQueryParameter] = Field(
        default_factory=list,
        serialization_alias='queryParameters',
        description='A list of query parameters to attach to every HTTP requests sent for this user',
    )
    body: Any | None = Field(
        default=None,
        description='A body to merge with the bodies of every HTTP requests sent for this user',
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


class UserRefresh(BaseModel):
    procedure: str | None = Field(
        default=None,
        description=(
            'Procedure to use to refresh the authentication.Defaults to the user procedure if not provided. '
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
    injections: list[TokenInjection] = Field(
        default_factory=list,
        description=(
            'List of injections to perform to create the refreshed authentication.'
            " If empty, the user's injections will be used to recreate an authentication object."
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


class UserAuthentication(BaseModel):
    procedure: str = Field(
        description=(
            'The name of the procedure to use to authenticate the user.'
            'This name MUST match the `name` field of a procedure in the `procedures` list in the '
            'multiauth configuration.'
        ),
    )
    injections: list[TokenInjection] = Field(
        description='List of variables injections to perform to create the authentication.',
    )


class User(BaseModel):
    name: str = Field(description='The name of the user')
    credentials: Credentials = Field(description='The parameters use to customize requests sent for the user')
    authentication: UserAuthentication = Field(
        description=(
            'The authentication parameters of the user, including the authentication procedure to follow'
            'and the description of how retrieved tokens should be injected in the user authentication result'
        ),
    )
    refresh: UserRefresh | None = Field(
        default=None,
        description='An optional refresh procedure to follow for the user',
    )

    @property
    def session_ttl_seconds(self) -> int | None:
        ttl_seconds = None

        # In case of a user-provided ttl for this user, use it instead of any ttl declared before
        if self.refresh is not None:
            ttl_seconds = self.refresh.session_seconds

        return ttl_seconds

    @staticmethod
    def from_user(user: 'User') -> 'User':
        return User(
            name=user.name,
            credentials=Credentials.from_credentials(user.credentials),
            authentication=user.authentication,
            refresh=user.refresh,
        )
