from typing import Any

from pydantic import BaseModel, Field

from multiauth.revamp.lib.http_core.entities import (
    HTTPCookie,
    HTTPHeader,
    HTTPQueryParameter,
)
from multiauth.revamp.store.injection import TokenInjection


class Credentials(BaseModel):
    username: str | None = Field(default=None)
    password: str | None = Field(default=None)
    headers: list[HTTPHeader] = Field(default_factory=list)
    cookies: list[HTTPCookie] = Field(default_factory=list)
    query_parameters: list[HTTPQueryParameter] = Field(default_factory=list, alias='queryParameters')
    body: Any | None = Field(default=None)

    @staticmethod
    def from_credentials(credentials: 'Credentials') -> 'Credentials':
        return Credentials(
            username=credentials.username,
            password=credentials.password,
            headers=credentials.headers,
            cookies=credentials.cookies,
            body=credentials.body,
        )


class User(BaseModel):
    name: str
    procedure: str
    credentials: Credentials
    injections: list[TokenInjection]

    @staticmethod
    def from_user(user: 'User') -> 'User':
        return User(
            name=user.name,
            procedure=user.procedure,
            credentials=Credentials.from_credentials(user.credentials),
            injections=user.injections,
        )
