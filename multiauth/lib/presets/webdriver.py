from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import ProcedureName, UserName, VariableName
from multiauth.lib.injection import TokenInjection
from multiauth.lib.presets.base import BasePreset, BaseUserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import TokenExtraction
from multiauth.lib.runners.webdriver.configuration import SeleniumProject
from multiauth.lib.runners.webdriver.runner import (
    SeleniumRunnerConfiguration,
    SeleniumScriptOptions,
    SeleniumScriptParameters,
)
from multiauth.lib.store.user import Credentials, User


class WebdriverUserPreset(BaseUserPreset, Credentials):
    username: UserName = Field(description='The arbitrary name that identifies the user.')
    project: SeleniumProject = Field(
        description=(
            'The Selenium project used to run the script. '
            'It is the one that contains the tests and commands to run. '
            'The project script can be generated using the Selenium IDE. '
            'See https://www.selenium.dev/selenium-ide/docs/en/introduction/getting-started/'
        ),
        examples=SeleniumProject.examples(),
    )


VARIABLE_NAME = 'token'


class WebdriverPreset(BasePreset):
    type: Literal['webdriver'] = 'webdriver'

    wait_for_seconds: int = Field(
        default=5,
        description=(
            'The number of seconds to wait at various steps of the script. '
            'For example when waiting for a page to load.'
        ),
        examples=[30],
    )

    extract: TokenExtraction = Field(
        description='The token extraction configuration used to extract the tokens from the HTTP response.',
        examples=TokenExtraction.examples(),
    )
    inject: TokenInjection = Field(
        description='The injection configuration used to inject the tokens into the HTTP requests.',
        examples=TokenInjection.examples(),
    )

    users: Sequence[WebdriverUserPreset] = Field(
        description='The list of users to generate tokens for.',
    )

    def to_procedure_configurations(self) -> list[ProcedureConfiguration]:
        procedures = list[ProcedureConfiguration]()

        for user in self.users:
            procedures.append(
                ProcedureConfiguration(
                    name=ProcedureName(self.slug + user.username),
                    injections=[
                        TokenInjection(
                            location=self.inject.location,
                            key=self.inject.key,
                            prefix=self.inject.prefix,
                            variable=VariableName(f'{user.username}-{VARIABLE_NAME}'),
                        ),
                    ],
                    operations=[
                        SeleniumRunnerConfiguration(
                            parameters=SeleniumScriptParameters(
                                project=user.project,
                                options=SeleniumScriptOptions(
                                    wait_for_seconds=self.wait_for_seconds,
                                ),
                            ),
                            extractions=[
                                TokenExtraction(
                                    location=self.extract.location,
                                    name=VariableName(f'{user.username}-{VARIABLE_NAME}'),
                                    key=self.extract.key,
                                    regex=self.extract.regex,
                                ),
                            ],
                        ),
                    ],
                ),
            )

        return procedures

    def to_users(self) -> list[User]:
        return [
            User(
                name=user.username,
                procedure=ProcedureName(self.slug + user.username),
            )
            for user in self.users
        ]
