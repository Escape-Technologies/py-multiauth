# pylint: disable=missing-docstring, too-few-public-methods

"""Abstract representation."""

from typing import Any

from multiauth.types.http import HTTPMethod
from multiauth.types.main import AuthTech, AuthType, JWTToken, Token


class IBase:

    """The base class for the user entity."""

    _auth_schema: str | None
    _auth_tech: AuthTech
    _auth_type: AuthType | None
    _credentials: dict[str, Any] | None
    _expired_token: Token | None
    _expires_in: float | None
    _headers: dict[str, Any] | None
    _refresh_token: Token | None
    _token_info: JWTToken | None
    _token: Token | None

    def reset(self) -> None:
        raise NotImplementedError()

    def set_token(self, token: Token | None, expires_in: float | None) -> None:
        raise NotImplementedError()

    def get_credentials(self) -> tuple[str, str]:
        raise NotImplementedError()

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError()


class IMultiAuth:

    _manager: Any
    _headers: dict[str, dict]
    _auths: dict

    @property
    def headers(self) -> dict[str, dict]:
        raise NotImplementedError()

    @property
    def users(self) -> dict:
        raise NotImplementedError()

    @property
    def schemas(self) -> dict:
        raise NotImplementedError()

    def sign(
        self,
        url: str,
        username: str,
        method: HTTPMethod,
        headers: dict[str, str],
        formatted_payload: Any,
    ) -> dict[str, str]:

        raise NotImplementedError

    def reauthenticate(
        self,
        username: str,
        headers: dict[str, str] | None = None,
        no_auth: bool = False,
    ) -> tuple[dict[str, str], str | None]:

        raise NotImplementedError

    def authenticate(
        self,
        username: str,
    ) -> tuple[dict[str, str], str]:

        raise NotImplementedError

    def authenticate_users(self) -> dict[str, Token | None]:

        raise NotImplementedError
