import logging
import os
from copy import deepcopy
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field
from selenium.webdriver import firefox
from seleniumwire import webdriver  # type: ignore[import-untyped]

from multiauth.helpers.base_model import StrictBaseModel
from multiauth.lib.audit.events.base import EventsList
from multiauth.lib.audit.events.events import (
    ExtractedVariableEvent,
    SeleniumScriptErrorEvent,
    SeleniumScriptLogEvent,
)
from multiauth.lib.http_core.entities import HTTPLocation
from multiauth.lib.runners.base import (
    BaseRunner,
    BaseRunnerConfiguration,
    BaseRunnerParameters,
    RunnerException,
)
from multiauth.lib.runners.http import TokenExtraction
from multiauth.lib.runners.webdriver.configuration import (
    SeleniumCommand,
    SeleniumProject,
    SeleniumTest,
)
from multiauth.lib.runners.webdriver.extractors import extract_token
from multiauth.lib.runners.webdriver.handler import SeleniumCommandHandler
from multiauth.lib.store.user import User
from multiauth.lib.store.variables import AuthenticationVariable, VariableName, interpolate_string


class SeleniumScriptOptions(StrictBaseModel):
    wait_for_seconds: int = Field(
        default=5,
        description=(
            'The number of seconds to wait at various steps of the script. '
            'For example when waiting for a page to load.'
        ),
        examples=[30],
    )

    proxy: str | None = Field(
        default=None,
        description=('The proxy used to run the script.'),
        examples=['http://my-proxy:8080'],
    )

    @staticmethod
    def examples() -> list:
        return [
            SeleniumScriptOptions(
                wait_for_seconds=30,
                proxy='http://my-proxy:8080',
            ),
            SeleniumScriptOptions(
                wait_for_seconds=5,
                proxy=None,
            ),
        ]


logger = logging.getLogger(__name__)


class SeleniumScriptParameters(BaseRunnerParameters):
    project: SeleniumProject = Field(
        description=(
            'The Selenium project used to run the script. '
            'It is the one that contains the tests and commands to run. '
            'The project script can be generated using the Selenium IDE. '
            'See https://www.selenium.dev/selenium-ide/docs/en/introduction/getting-started/'
        ),
        examples=SeleniumProject.examples(),
    )
    options: SeleniumScriptOptions = Field(
        description=('The options of the Selenium script.'),
        examples=SeleniumScriptOptions.examples(),
    )

    @staticmethod
    def examples() -> list:
        return [
            SeleniumScriptParameters(
                project=SeleniumProject(
                    tests=[
                        SeleniumTest(
                            id='a2b6cac88640424d863182874cbf8ca0',
                            name='test',
                            commands=[
                                SeleniumCommand(
                                    id='a2b6cac88640424d863182874cbf8ca0',
                                    targets=[['css', 'body']],
                                    value='',
                                    command='open',
                                    target='https://example.com',
                                ),
                            ],
                        ),
                    ],
                ),
                options=SeleniumScriptOptions(),
            ),
        ]


class SeleniumRunnerConfiguration(BaseRunnerConfiguration):
    tech: Literal['selenium'] = 'selenium'
    parameters: SeleniumScriptParameters = Field(
        description=('The parameters of the Selenium operation.'),
        examples=SeleniumScriptParameters.examples(),
    )

    def get_runner(self) -> 'SeleniumRunner':
        return SeleniumRunner(self)

    @staticmethod
    def examples() -> list:
        return [
            SeleniumRunnerConfiguration(
                extractions=[
                    TokenExtraction(
                        key='access_token',
                        location=HTTPLocation.BODY,
                        regex='access_token=(.*?)&',
                        name=VariableName('access_token'),
                    ),
                ],
                parameters=SeleniumScriptParameters(
                    project=SeleniumProject(
                        tests=[
                            SeleniumTest(
                                id='a2b6cac88640424d863182874cbf8ca0',
                                name='test',
                                commands=[
                                    SeleniumCommand(
                                        id='a2b6cac88640424d863182874cbf8ca0',
                                        targets=[['css', 'body']],
                                        value='',
                                        command='open',
                                        target='https://example.com',
                                    ),
                                ],
                            ),
                        ],
                    ),
                    options=SeleniumScriptOptions(),
                ),
            ).dict(exclude_defaults=True),
        ]


class SeleniumRunner(BaseRunner[SeleniumRunnerConfiguration]):
    selenium_configuration: SeleniumRunnerConfiguration

    def __init__(self, configuration: SeleniumRunnerConfiguration) -> None:
        self.selenium_configuration = configuration
        super().__init__(configuration)

    @property
    def visited_hosts(self) -> set[str]:
        visited_hosts = set()
        for test in self.selenium_configuration.parameters.project.tests:
            for command in test.commands:
                if command.command == 'open':
                    try:
                        _, host, _, _, _, _ = urlparse(command.target)
                        visited_hosts.add(host)
                    except Exception as e:
                        logger.error(f'Failed to parse URL {command.target}')
                        logger.error(e)
                        continue
        return visited_hosts

    def run(self, _user: User) -> tuple[list[AuthenticationVariable], EventsList, RunnerException | None]:
        driver = self.setup_driver()
        events = EventsList()

        logger.info(f'Visiting {len(self.visited_hosts)} hosts: {", ".join(self.visited_hosts)}')
        events.append(
            SeleniumScriptLogEvent(
                message=(
                    f'Visiting {len(self.visited_hosts)} hosts: {", ".join(self.visited_hosts)}.'
                    ' Requests targeting other will not be reported.'
                ),
            ),
        )

        for test in self.selenium_configuration.parameters.project.tests:
            logger.info(f'Running test {test.name}')
            events.append(SeleniumScriptLogEvent(message=f'Running test `{test.name}`'))
            handler = SeleniumCommandHandler(
                driver,
                self.selenium_configuration.parameters.options.wait_for_seconds,
                self.visited_hosts,
            )

            for command in test.commands:
                logger.info(f'Running command {command.id} - {command.command}')
                command_events, exception = handler.run_command(command)
                logger.info(f'Command {command.id} finished')
                events.extend(command_events)
                if exception:
                    logger.error(f'Aborting test due to an exception: {exception}')
                    events.append(SeleniumScriptErrorEvent(message='Aborting test due to an exception'))
                    break

        requests = deepcopy(driver.requests)
        driver.quit()

        variables: list[AuthenticationVariable] = []

        for extraction in self.selenium_configuration.extractions:
            try:
                token = extract_token(
                    extraction.location,
                    extraction.key,
                    extraction.regex,
                    requests,
                )
                variable = AuthenticationVariable(name=extraction.slug, value=token)
                events.append(ExtractedVariableEvent(location=extraction.location, variable=variable))
                variables.append(variable)
            except Exception as e:
                events.append(
                    SeleniumScriptErrorEvent(
                        message='Failed to extract token due to an exception',
                        from_exception=str(e),
                    ),
                )
                return variables, events, RunnerException('Failed to extract token due to an exception')

        return variables, events, None

    def setup_driver(self) -> webdriver.Firefox:
        firefox_options = firefox.options.Options()
        firefox_options.add_argument('--no-sandbox')
        firefox_options.add_argument('--headless')
        firefox_options.add_argument('--disable-gpu')
        firefox_options.set_preference('browser.download.folderList', 2)
        firefox_options.set_preference('browser.download.manager.showWhenStarting', False)
        firefox_options.set_preference('browser.download.dir', os.getcwd())
        firefox_options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

        driver = webdriver.Firefox(options=firefox_options)

        if proxy := self.selenium_configuration.parameters.options.proxy:
            logger.info(f'Webdriver uses proxy {proxy}')
            driver.proxy = {'http': proxy, 'https': proxy}

        return driver

    def interpolate(self, variables: list[AuthenticationVariable]) -> 'SeleniumRunner':
        selenium_configuration_str = self.selenium_configuration.model_dump_json()
        selenium_configuration_str = interpolate_string(selenium_configuration_str, variables)
        selenium_configuration = SeleniumRunnerConfiguration.model_validate_json(selenium_configuration_str)

        return SeleniumRunner(selenium_configuration)
