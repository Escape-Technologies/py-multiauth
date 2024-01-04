import os
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field
from selenium.webdriver import firefox
from seleniumwire import webdriver  # type: ignore[import-untyped]

from multiauth.revamp.lib.audit.events.base import Event
from multiauth.revamp.lib.audit.events.events import (
    ExtractedVariableEvent,
    SeleniumScriptErrorEvent,
    SeleniumScriptLogEvent,
)
from multiauth.revamp.lib.runners.base import (
    BaseExtraction,
    BaseRunner,
    BaseRunnerConfiguration,
    BaseRunnerParameters,
    RunnerException,
)
from multiauth.revamp.lib.runners.webdriver.configuration import (
    SeleniumProject,
)
from multiauth.revamp.lib.runners.webdriver.extractors import WebdriverTokenLocationType, extract_token
from multiauth.revamp.lib.runners.webdriver.handler import SeleniumCommandHandler
from multiauth.revamp.lib.store.user import User
from multiauth.revamp.lib.store.variables import AuthenticationVariable, interpolate_string


class SeleniumScriptOptions(BaseModel):
    token_lifetime: int | None = Field(default=None)

    proxy: str | None = None


@dataclass
class SeleniumScriptParameters(BaseRunnerParameters):
    project: SeleniumProject
    options: SeleniumScriptOptions


class SeleniumExtraction(BaseExtraction):
    extract_location: WebdriverTokenLocationType
    extract_regex: str
    extract_match_index: int | None = Field(default=None)


class SeleniumRunnerConfiguration(BaseRunnerConfiguration):
    tech: Literal['selenium'] = 'selenium'
    extractions: list[SeleniumExtraction]
    parameters: SeleniumScriptParameters

    def get_runner(self) -> 'SeleniumRunner':
        return SeleniumRunner(self)


class SeleniumRunner(BaseRunner[SeleniumRunnerConfiguration]):
    selenium_configuration: SeleniumRunnerConfiguration

    def __init__(self, configuration: SeleniumRunnerConfiguration) -> None:
        self.selenium_configuration = configuration
        super().__init__(configuration)

    def run(self, _user: User) -> tuple[list[AuthenticationVariable], list[Event], RunnerException | None]:
        driver = self.setup_driver()
        events: list[Event] = []

        for test in self.selenium_configuration.parameters.project.tests:
            events.append(SeleniumScriptLogEvent(message=f'Running test `{test.name}`'))
            handler = SeleniumCommandHandler(driver)

            for command in test.commands:
                command_events, exception = handler.run_command(command)
                events.extend(command_events)
                if exception:
                    events.append(SeleniumScriptErrorEvent(message='Aborting test due to an exception'))
                    break

        driver.quit()

        variables: list[AuthenticationVariable] = []

        for extraction in self.selenium_configuration.extractions:
            try:
                token = extract_token(
                    extraction.extract_location,
                    extraction.extract_regex,
                    extraction.extract_match_index,
                    driver.requests,
                )
                variable = AuthenticationVariable(name=extraction.name, value=token)
                events.append(ExtractedVariableEvent(variable=variable))
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
            driver.proxy = {'http': proxy, 'https': proxy}

        return driver

    def interpolate(self, variables: list[AuthenticationVariable]) -> 'SeleniumRunner':
        selenium_configuration_str = self.selenium_configuration.model_dump_json()
        selenium_configuration_str = interpolate_string(selenium_configuration_str, variables)
        selenium_configuration = SeleniumRunnerConfiguration.model_validate_json(selenium_configuration_str)

        return SeleniumRunner(selenium_configuration)
