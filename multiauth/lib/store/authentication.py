import abc
import datetime

from pydantic import Field

from multiauth.helpers.base_model import StrictBaseModel
from multiauth.lib.http_core.entities import HTTPCookie, HTTPHeader, HTTPQueryParameter
from multiauth.lib.http_core.mergers import merge_cookies, merge_headers, merge_query_parameters
from multiauth.lib.store.user import Credentials, UserName


class Authentication(StrictBaseModel):
    headers: list[HTTPHeader] = Field(default_factory=list)
    cookies: list[HTTPCookie] = Field(default_factory=list)
    query_parameters: list[HTTPQueryParameter] = Field(default_factory=list)

    @property
    def all_headers(self) -> dict[str, str]:
        return {header.name: header.str_value for header in self.headers} | {
            'Cookies': HTTPCookie.serialize(self.cookies),
        }

    @staticmethod
    def empty() -> 'Authentication':
        return Authentication()

    @staticmethod
    def from_credentials(credentials: Credentials) -> 'Authentication':
        authentication = Authentication.empty()
        authentication.headers = credentials.headers
        authentication.cookies = credentials.cookies
        authentication.query_parameters = credentials.query_parameters

        return authentication

    def __str__(self) -> str:
        authentication_str = ''
        if len(self.headers) > 0:
            authentication_str += 'Headers:\n'
            for header in self.headers:
                authentication_str += f'- {header.name}: {header.str_value}\n'
        else:
            authentication_str += 'No headers\n'

        if len(self.cookies) > 0:
            authentication_str += 'Cookies:\n'
            for cookie in self.cookies:
                authentication_str += f'\t- {cookie.name}: {cookie.str_value}\n'
        else:
            authentication_str += 'No cookies\n'

        if len(self.query_parameters) > 0:
            authentication_str += 'Query Parameters:\n'
            for query_parameter in self.query_parameters:
                authentication_str += f'\t- {query_parameter.name}: {query_parameter.str_value}\n'
        else:
            authentication_str += 'No query parameters\n'

        return authentication_str

    @staticmethod
    def merge(auth_a: 'Authentication', auth_b: 'Authentication') -> 'Authentication':
        return Authentication(
            headers=merge_headers(auth_a.headers, auth_b.headers),
            cookies=merge_cookies(auth_a.cookies, auth_b.cookies),
            query_parameters=merge_query_parameters(auth_a.query_parameters, auth_b.query_parameters),
        )


class AuthenticationStoreException(Exception, abc.ABC):
    pass


class ExpiredAuthenticationException(AuthenticationStoreException):
    user_name: str
    expired_at: datetime.datetime

    def __init__(self, user_name: str, expired_at: datetime.datetime) -> None:
        self.user_name = user_name
        self.expired_at = expired_at

    def __str__(self) -> str:
        return f'Authentication for user `{self.user_name}` expired at {self.expired_at}.'


class UnauthenticatedUserException(AuthenticationStoreException):
    user_name: str

    def __init__(self, user_name: str) -> None:
        self.user_name = user_name

    def __str__(self) -> str:
        return f'User `{self.user_name}` is not authenticated.'


class AuthenticationStore:
    """
    Store for user authentication objects.
    """

    __store: dict[UserName, list[tuple[Authentication, datetime.datetime]]]  # list is for history
    __refresh_counts: dict[UserName, int]

    def __init__(self) -> None:
        self.__store = {}
        self.__refresh_counts = {}

    def expire(self, user_name: UserName) -> None:
        """
        Mark the user as immediately expired.

        - Raises an `UnauthenticatedUserException` if no authentication object has been provided yet for this user
        """

        authentication, _expiration = self.get(user_name)
        self.__store[user_name].append((authentication, datetime.datetime.now()))

    def is_expired(self, user_name: UserName) -> bool:
        """
        Assess the expiration status of an user.

        - Raises an `UnauthenticatedUserException` if no authentication object has been provided yet for this user
        """
        _, expiration = self.get(user_name)
        return expiration < datetime.datetime.now()

    def get_history(self, user_name: UserName) -> list[tuple[Authentication, datetime.datetime]]:
        """
        Retrive all the authentication objects of an user.
        """
        records = self.__store.get(user_name)
        if not records:
            raise UnauthenticatedUserException(user_name)
        return records

    def get(self, user_name: UserName) -> tuple[Authentication, datetime.datetime]:
        """
        Retrive the authentication object of an user, with its expiration datetime.

        - Raises an `UnauthenticatedUserException` if no authentication object has been provided yet for this user
        """
        return self.get_history(user_name)[-1]  # last record is the current one

    def store(self, user_name: UserName, authentication: Authentication, expiration: datetime.datetime) -> int:
        """
        Store an authentication object with an expiration time for the provided user_name.
        Return an integer describing the number of authentication objects that have already been store for this user.
        """
        if user_name in self.__refresh_counts:
            self.__refresh_counts[user_name] += 1
        else:
            self.__refresh_counts[user_name] = 0

        if user_name not in self.__store:
            self.__store[user_name] = []

        self.__store[user_name].append((authentication, expiration))
        return self.__refresh_counts[user_name]
