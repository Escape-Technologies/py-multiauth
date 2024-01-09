import abc
import datetime

from pydantic import BaseModel, Field

from multiauth.lib.audit.events.base import EventsList
from multiauth.lib.audit.events.events import InjectedVariableEvent
from multiauth.lib.http_core.entities import HTTPCookie, HTTPHeader, HTTPLocation, HTTPQueryParameter
from multiauth.lib.http_core.mergers import merge_cookies, merge_headers, merge_query_parameters
from multiauth.lib.store.injection import TokenInjection
from multiauth.lib.store.user import Credentials, UserName
from multiauth.lib.store.variables import AuthenticationVariable


class Authentication(BaseModel):
    headers: list[HTTPHeader] = Field(default_factory=list)
    cookies: list[HTTPCookie] = Field(default_factory=list)
    query_parameters: list[HTTPQueryParameter] = Field(default_factory=list)

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

    @staticmethod
    def inject(
        injection: TokenInjection,
        variables: list[AuthenticationVariable],
    ) -> tuple['Authentication', EventsList]:
        authentication = Authentication.empty()
        events = EventsList()

        if len(variables) == 0:
            return authentication, events

        variable: AuthenticationVariable | None = None
        if injection.variable is None:
            variable = variables[0]
        else:
            variable = next((v for v in variables if v.name == injection.variable), None)

        if variable is None:
            return authentication, events

        if injection.location == HTTPLocation.HEADER:
            header = HTTPHeader(
                name=injection.key,
                values=[f'{injection.prefix or ""}{variable.value}'],
            )
            authentication.headers.append(header)
            events.append(InjectedVariableEvent(variable=variable, location=HTTPLocation.HEADER, target=injection.key))
        elif injection.location == HTTPLocation.COOKIE:
            cookie = HTTPCookie(
                name=injection.key,
                values=[f'{injection.prefix or ""}{variable.value}'],
            )
            authentication.cookies.append(cookie)
            events.append(InjectedVariableEvent(variable=variable, location=HTTPLocation.COOKIE, target=injection.key))
        elif injection.location == HTTPLocation.QUERY:
            query_parameter = HTTPQueryParameter(
                name=injection.key,
                values=[f'{injection.prefix or ""}{variable.value}'],
            )
            authentication.query_parameters.append(query_parameter)
            events.append(InjectedVariableEvent(variable=variable, location=HTTPLocation.QUERY, target=injection.key))
        return authentication, events

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

    __store: dict[UserName, tuple[Authentication, datetime.datetime]]
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
        self.__store[user_name] = (authentication, datetime.datetime.now())

    def is_expired(self, user_name: UserName) -> bool:
        """
        Assess the expiration status of an user.

        - Raises an `UnauthenticatedUserException` if no authentication object has been provided yet for this user
        """
        _, expiration = self.get(user_name)
        return expiration < datetime.datetime.now()

    def get(self, user_name: UserName) -> tuple[Authentication, datetime.datetime]:
        """
        Retrive the authentication object of an user, with its expiration datetime.

        - Raises an `UnauthenticatedUserException` if no authentication object has been provided yet for this user
        """
        record = self.__store.get(user_name)
        if not record:
            raise UnauthenticatedUserException(user_name)
        authentication, expiration = record

        return authentication, expiration

    def store(self, user_name: UserName, authentication: Authentication, expiration: datetime.datetime) -> int:
        """
        Store an authentication object with an expiration time for the provided user_name.
        Return an integer describing the number of authentication objects that have already been store for this user.
        """
        if user_name in self.__refresh_counts:
            self.__refresh_counts[user_name] += 1
        else:
            self.__refresh_counts[user_name] = 0

        self.__store[user_name] = (authentication, expiration)
        return self.__refresh_counts[user_name]
