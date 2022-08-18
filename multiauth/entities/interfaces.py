# pylint: disable=missing-docstring, too-few-public-methods

"""Abstract representation."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

from multiauth.entities.http import HTTPMethod
from multiauth.entities.main import AuthTech, AuthType, JWTToken, Token


class IUser(ABC):

    """The base class for the user entity."""

    _auth_schema: Optional[str]
    _auth_tech: AuthTech
    _auth_type: Optional[AuthType]
    _credentials: Optional[Dict[str, Any]]
    _expired_token: Optional[Token]
    _expires_in: Optional[float]
    _headers: Optional[Dict[str, Any]]
    _refresh_token: Optional[Token]
    _token_info: Optional[JWTToken]
    _token: Optional[Token]

    @abstractmethod
    def reset(self) -> None:
        ...

    @abstractmethod
    def set_token(
        self,
        token: Optional[Token],
        expires_in: Optional[float],
    ) -> None:
        ...

    @abstractmethod
    def get_credentials(self) -> Tuple[str, str]:
        ...

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        ...


class IMultiAuth(ABC):

    _logger: logging.Logger
    _authrc: Optional[str]

    _manager: Any
    _headers: Dict[str, Dict]
    _auths: Dict

    @property
    @abstractmethod
    def headers(self) -> Dict[str, Dict]:
        ...

    @property
    @abstractmethod
    def auths(self) -> Dict:
        ...

    @property
    @abstractmethod
    def users(self) -> Dict:
        ...

    @property
    @abstractmethod
    def schemas(self) -> Dict:
        ...

    @abstractmethod
    def sign(
        self,
        url: str,
        username: str,
        method: HTTPMethod,
        headers: Dict[str, str],
        formatted_payload: Any,
    ) -> Dict[str, str]:
        ...

    @abstractmethod
    def reauthenticate(
        self,
        username: str,
        additional_headers: Optional[Dict[str, str]] = None,
        no_auth: bool = False,
    ) -> Tuple[Dict[str, str], Optional[str]]:
        ...

    @abstractmethod
    def authenticate(
        self,
        username: str,
    ) -> Tuple[Dict[str, str], str]:
        ...

    @abstractmethod
    def authenticate_users(self) -> Dict[str, Optional[Token]]:
        ...
