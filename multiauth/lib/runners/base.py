import abc
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

from multiauth.lib.audit.events.base import EventsList
from multiauth.lib.store.user import User
from multiauth.lib.store.variables import AuthenticationVariable, VariableName

RunnerType = Literal['http', 'basic', 'graphql', 'selenium', 'digest']


class BaseRunnerParameters(BaseModel, abc.ABC):
    pass


class BaseExtraction(BaseModel, abc.ABC):
    name: VariableName = Field(description=('The name of the variable to store the extracted value in'))


ExtractionType = TypeVar('ExtractionType', bound=BaseExtraction)
RunnerParametersType = TypeVar('RunnerParametersType', bound=BaseRunnerParameters)


class BaseRunnerConfiguration(BaseModel, abc.ABC, Generic[ExtractionType, RunnerParametersType]):
    tech: RunnerType
    parameters: RunnerParametersType
    extractions: list[ExtractionType] = Field(default_factory=list)

    @abc.abstractmethod
    def get_runner(self) -> 'BaseRunner':
        ...


T = TypeVar('T', bound=BaseRunnerConfiguration)


class RunnerException(Exception):
    pass


class BaseRunner(abc.ABC, Generic[T]):
    request_configuration: T

    def __init__(self, request_configuration: T) -> None:
        self.request_configuration = request_configuration

    @abc.abstractmethod
    def run(self, user: User) -> tuple[list[AuthenticationVariable], EventsList, RunnerException | None]:
        ...

    @abc.abstractmethod
    def interpolate(self, variables: list[AuthenticationVariable]) -> 'BaseRunner':
        ...
