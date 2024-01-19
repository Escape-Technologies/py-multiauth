from typing import Literal, Sequence

from pydantic import Field

from multiauth.lib.entities import ProcedureName, UserName, VariableName
from multiauth.lib.http_core.entities import HTTPCookie, HTTPHeader, HTTPLocation
from multiauth.lib.injection import TokenInjection
from multiauth.lib.presets.base import BasePreset, BasePresetDoc, BaseUserPreset
from multiauth.lib.procedure import ProcedureConfiguration
from multiauth.lib.runners.http import TokenExtraction
from multiauth.lib.runners.webdriver.configuration import SeleniumCommand, SeleniumProject, SeleniumTest
from multiauth.lib.runners.webdriver.runner import (
    SeleniumRunnerConfiguration,
    SeleniumScriptOptions,
    SeleniumScriptParameters,
)
from multiauth.lib.store.user import Credentials, User


class WebdriverUserPreset(BaseUserPreset):
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

    @staticmethod
    def _doc() -> BasePresetDoc:
        return BasePresetDoc(
            title='Webdriver',
            description="""The 'Webdriver' authentication preset is designed for scenarios where traditional authentication methods are not feasible, and it relies on Selenium-based web automation:

- **Selenium Project Integration**: Utilizes Selenium Projects, created via Selenium IDE, to automate the login process on a web interface.
- **Dynamic Interaction**: Capable of handling complex login procedures including multi-step forms, CAPTCHAs, and JavaScript-based interactions.
- **Token Extraction and Injection**: Extracts authentication tokens from the web automation flow and injects them into HTTP requests.
- **Consideration**: Preferred as a last-resort option due to the overhead and potential fragility of maintaining Selenium scripts.

This preset is particularly useful when other forms of API-based authentication are not available, requiring direct interaction with web interfaces for authentication.""",  # noqa: E501
            examples=[
                WebdriverPreset(
                    type='webdriver',
                    wait_for_seconds=30,
                    extract=TokenExtraction(
                        location=HTTPLocation.QUERY,
                        key='',
                        regex='example-portal.*portal-session-id=([^&]*)',
                    ),
                    inject=TokenInjection(
                        location=HTTPLocation.HEADER,
                        key='Authorization',
                        prefix='Bearer ',
                    ),
                    users=[
                        WebdriverUserPreset(
                            username=UserName('user'),
                            project=SeleniumProject(
                                tests=[
                                    SeleniumTest(
                                        id='aec1dcca-65ca-4e09-82a6-8da7bbddbde0',
                                        name='Example Selenium Sequence',
                                        commands=[
                                            SeleniumCommand(
                                                id='bb671e84-0d81-40da-92ad-4086ec483f6d',
                                                command='open',
                                                target='https://auth.example.com/signin/?return=/setup/payment-types/',
                                                targets=[],
                                                value='',
                                            ),
                                            SeleniumCommand(
                                                id='6406387f-c3bf-453c-8dee-561a548f6c42',
                                                value='username@example.com',
                                                target='name=username',
                                                command='type',
                                                targets=[
                                                    ['name=username', 'name'],
                                                    ['css=.vd-field:nth-child(1) .vd-input', 'css:finder'],
                                                    ["xpath=//input[@name='username']", 'xpath:attributes'],
                                                    [
                                                        "xpath=//div[@id='react-root']/section/main/div/div/div/div/div/div[2]/form/div/div[2]/input",
                                                        'xpath:idRelative',
                                                    ],
                                                    ['xpath=//input', 'xpath:position'],
                                                ],
                                            ),
                                            SeleniumCommand(
                                                id='adf71a06-33cc-4e89-b69b-0e324edaa314',
                                                value='C0mplexPassWord!',
                                                target='name=password',
                                                command='type',
                                                targets=[
                                                    ['name=password', 'name'],
                                                    ['css=.vd-field:nth-child(2) .vd-input', 'css:finder'],
                                                    ["xpath=//input[@name='password']", 'xpath:attributes'],
                                                    [
                                                        "xpath=//div[@id='react-root']/section/main/div/div/div/div/div/div[2]/form/div[2]/div[2]/input",
                                                        'xpath:idRelative',
                                                    ],
                                                    ['xpath=//div[2]/div[2]/input', 'xpath:position'],
                                                ],
                                            ),
                                            SeleniumCommand(
                                                id='0c18a7ca-b347-4402-adf7-18c02b54d326',
                                                value='',
                                                target='name=signin_submit',
                                                command='click',
                                                targets=[
                                                    ['name=signin_submit', 'name'],
                                                    ['css=.vd-btn', 'css:finder'],
                                                    ["xpath=//button[@name='signin_submit']", 'xpath:attributes'],
                                                    [
                                                        "xpath=//div[@id='react-root']/section/main/div/div/div/div/div/div[2]/form/div[3]/button",
                                                        'xpath:idRelative',
                                                    ],
                                                    ['xpath=//button', 'xpath:position'],
                                                    ["xpath=//button[contains(.,'Sign in')]", 'xpath:innerText'],
                                                ],
                                            ),
                                            SeleniumCommand(
                                                id='552d7f74-25bf-4213-aba3-b0c5b598f3b9',
                                                command='wait',
                                                target='request_url_contains=portal-session-id',
                                                targets=[],
                                                value='30',
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
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
                credentials=Credentials(
                    headers=HTTPHeader.from_dict(user.headers),
                    cookies=HTTPCookie.from_dict(user.cookies),
                ),
            )
            for user in self.users
        ]
