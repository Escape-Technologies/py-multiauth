import abc
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

from multiauth.revamp.lib.http_core.entities import HTTPRequest, HTTPResponse
from multiauth.revamp.store.user import User
from multiauth.revamp.store.variables import AuthenticationVariable

AuthenticationType = Literal['http', 'basic', 'graphql']


class BaseRequestParameters(BaseModel, abc.ABC):
    pass


class BaseExtraction(BaseModel, abc.ABC):
    pass


ExtractionType = TypeVar('ExtractionType', bound=BaseExtraction)
RequestParameterType = TypeVar('RequestParameterType', bound=BaseRequestParameters)


class BaseRequestConfiguration(BaseModel, abc.ABC, Generic[ExtractionType, RequestParameterType]):
    tech: AuthenticationType
    parameters: RequestParameterType
    extractions: list[ExtractionType] = Field(default_factory=list)

    @abc.abstractmethod
    def get_runner(self) -> 'BaseRequestRunner':
        ...


T = TypeVar('T', bound=BaseRequestConfiguration)


class BaseRequestRunner(abc.ABC, Generic[T]):
    request_configuration: T

    @abc.abstractmethod
    def request(self, user: User) -> tuple[HTTPRequest, HTTPResponse] | None:
        ...

    @abc.abstractmethod
    def extract(self, response: HTTPResponse) -> list[AuthenticationVariable]:
        ...
