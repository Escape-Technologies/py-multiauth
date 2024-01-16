import abc
from typing import Generic, Literal, TypeVar

from multiauth.helpers.base_model import StrictBaseModel
from multiauth.lib.audit.events.base import EventsList
from multiauth.lib.extraction import TokenExtraction
from multiauth.lib.store.user import User
from multiauth.lib.store.variables import AuthenticationVariable

RunnerType = Literal['http', 'basic', 'graphql', 'selenium', 'digest']


class BaseRunnerParameters(StrictBaseModel, abc.ABC):
    pass


RunnerParametersType = TypeVar('RunnerParametersType', bound=BaseRunnerParameters)


class BaseRunnerConfiguration(StrictBaseModel, abc.ABC, Generic[RunnerParametersType]):
    tech: RunnerType
    parameters: RunnerParametersType
    extractions: list[TokenExtraction]

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
