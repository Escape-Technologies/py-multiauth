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
        pass

    @abstractmethod
    def set_token(
        self,
        token: Optional[Token],
        expires_in: Optional[float],
    ) -> None:
        pass

    @abstractmethod
    def get_credentials_pair(self) -> Tuple[str, str]:
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass


class IMultiAuth(ABC):
    _logger: logging.Logger
    _authrc: Optional[str]

    _manager: Any
    _headers: Dict[str, Dict]
    _auths: Dict

    @property
    @abstractmethod
    def headers(self) -> Dict[str, Dict]:
        pass

    @property
    @abstractmethod
    def auths(self) -> Dict:
        pass

    @property
    @abstractmethod
    def users(self) -> Dict:
        pass

    @property
    @abstractmethod
    def schemas(self) -> Dict:
        pass

    @abstractmethod
    def sign(
        self,
        url: str,
        username: str,
        method: HTTPMethod,
        headers: Dict[str, str],
        formatted_payload: Any,
    ) -> Dict[str, str]:
        pass

    @abstractmethod
    def reauthenticate(
        self,
        username: str,
        additional_headers: Optional[Dict[str, str]] = None,
        public: bool = False,
    ) -> Tuple[Dict[str, str], Optional[str]]:
        pass

    @abstractmethod
    def authenticate(
        self,
        username: str,
    ) -> Tuple[Dict[str, str], str]:
        pass

    @abstractmethod
    def authenticate_users(self) -> Dict[str, Optional[Token]]:
        pass
