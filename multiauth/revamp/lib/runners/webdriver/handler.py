import re
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver  # type: ignore[import-untyped]

from multiauth.revamp.lib.audit.events.base import Event
from multiauth.revamp.lib.audit.events.events import (  # type: ignore[import-untyped]
    SeleniumScriptErrorEvent,
    SeleniumScriptLogEvent,
)
from multiauth.revamp.lib.runners.base import RunnerException
from multiauth.revamp.lib.runners.webdriver.configuration import SeleniumCommand
from multiauth.revamp.lib.runners.webdriver.transformers import (  # type: ignore[import-untyped]
    target_to_selector_value,
    target_to_value,
)


class SeleniumCommandException(RunnerException):
    base_exception: Exception | None

    def __init__(self, message: str, base_exception: Exception | None = None) -> None:
        self.base_exception = base_exception
        super().__init__(message)


class SeleniumCommandHandler:
    driver: webdriver.Firefox

    wait_for_seconds: int
    pooling_interval: float

    def __init__(self, driver: webdriver.Firefox) -> None:
        self.driver = driver
        self.wait_for_seconds = 5
        self.pooling_interval = 0.5

    def run_command(self, command: SeleniumCommand) -> tuple[list[Event], SeleniumCommandException | None]:
        match command.command:
            case 'open':
                return self.open(command)
            case 'setWindowSize':
                return self.set_window_size(command)
            case 'click':
                return self.click(command)
            case 'type':
                return self.type(command)
            case 'mouseOver':
                return self.mouse_over(command)
            case 'mouseOut':
                return self.mouse_out(command)
            case 'wait':
                return self.wait(command)
            case 'selectFrame':
                return self.select_frame(command)

        message = f'Unhandled command `{command.command}`'
        error = SeleniumCommandException(message=message)
        event = SeleniumScriptErrorEvent(message=message, from_exception=str(error))
        return [event], error

    def find_element(self, selector: str, value: str) -> WebElement:
        wait = WebDriverWait(self.driver, self.wait_for_seconds)
        return wait.until(EC.presence_of_element_located((selector, value)))

    def safe_click(self, selector: str, value: str) -> tuple[list[Event], SeleniumCommandException | None]:
        tries = 0
        events: list[Event] = []
        for _ in range(10):
            try:
                tries += 1
                self.find_element(selector, value).click()
                events.append(
                    SeleniumScriptLogEvent(
                        severity='info',
                        message=f'Clicked `{selector}`.`{value}` after {tries} tries',
                    ),
                )
                return events, None
            except Exception as e:
                time.sleep(1)
                last_error = e

        events.append(
            SeleniumScriptErrorEvent(
                severity='error',
                message=f'Failed to click element `{selector}` after {tries} tries',
                from_exception=str(last_error),
            ),
        )
        return events, SeleniumCommandException(
            f'Failed to click element `{selector}` after {tries} tries',
            base_exception=last_error,
        )

    def safe_switch_to_frame(self, selector: int | str) -> tuple[list[Event], SeleniumCommandException | None]:
        tries = 0
        events: list[Event] = []
        for _ in range(10):
            try:
                tries += 1
                self.driver.switch_to.frame(selector)
                events.append(
                    SeleniumScriptLogEvent(
                        severity='info',
                        message=f'Switched to frame `{selector}`',
                    ),
                )
                return events, None
            except Exception as e:
                time.sleep(1)
                last_error = e

        message = f'Failed to switch to frame `{selector}` after {tries} retries'
        error = SeleniumCommandException(
            message,
            base_exception=last_error,
        )
        events.append(
            SeleniumScriptErrorEvent(
                severity='error',
                message=message,
                from_exception=str(error),
            ),
        )
        return events, error

    def open(self, command: SeleniumCommand) -> tuple[list[Event], SeleniumCommandException | None]:
        events: list[Event] = []
        url = command.target
        try:
            self.driver.get(url)
            events.append(SeleniumScriptLogEvent(message=f'Opened URL `{url}`'))
            return events, None
        except Exception as e:
            events.append(SeleniumScriptErrorEvent(message=f'Failed to open URL `{url}`', from_exception=str(e)))
            return events, SeleniumCommandException(f'Failed to open URL `{url}`: {e}', base_exception=e)

    def set_window_size(self, command: SeleniumCommand) -> tuple[list[Event], SeleniumCommandException | None]:
        events: list[Event] = []

        width, height = command.target.split('x')

        try:
            self.driver.set_window_size(int(width), int(height))
            events.append(SeleniumScriptLogEvent(message=f'Set window size to `{width}x{height}`'))
            return events, None
        except Exception as e:
            message = f'Failed to set window size to `{width}x{height}`'
            events.append(SeleniumScriptErrorEvent(message=message, from_exception=str(e)))
            return events, SeleniumCommandException(message, base_exception=e)

    def click(
        self,
        command: SeleniumCommand,
        retries: int | None = None,
    ) -> tuple[list[Event], SeleniumCommandException | None]:
        events: list[Event] = []
        exception: Exception | None = None

        for target_pair in command.targets:
            try:
                selector, value = target_to_selector_value(target_pair)
                click_events, exception = self.safe_click(selector, value)
                events.extend(click_events)
                if exception is not None:
                    return events, exception
            except Exception as e:
                message = f'Failed to execute click `{command.id}`.`{target_pair}`'
                events.append(
                    SeleniumScriptErrorEvent(message=message, from_exception=str(e)),
                )

        if retries is None:
            self.driver.implicitly_wait(10)
            events.append(SeleniumScriptLogEvent(message='Retrying click command', severity='warning'))
            return self.click(command, retries=1)

        return events, SeleniumCommandException(f'Failed to execute click `{command.id}`', base_exception=exception)

    def select_frame(self, command: SeleniumCommand) -> tuple[list[Event], SeleniumCommandException | None]:
        events: list[Event] = []
        target = command.target
        exception: SeleniumCommandException | None = None

        try:
            if target.startswith('index='):
                index = int(target_to_value(target))
                switch_events, exception = self.safe_switch_to_frame(index)
                events.extend(switch_events)

            # Check if target is a name or ID
            elif '=' not in target:  # Assumes no "=" character in frame names or IDs
                switch_events, exception = self.safe_switch_to_frame(target)
                events.extend(switch_events)

            else:
                message = f'Unhandled selector type for selectFrame: {target}'
                events.append(SeleniumScriptErrorEvent(message=message))
                exception = SeleniumCommandException(message)

        except Exception as e:
            message = f'Failed to execute type `{command.id}`.`{target}`'
            exception = SeleniumCommandException(message=message, base_exception=e)

        return events, exception

    def type(self, command: SeleniumCommand) -> tuple[list[Event], SeleniumCommandException | None]:
        events: list[Event] = []
        exception: SeleniumCommandException | None = None

        for target_pair in command.targets:
            try:
                selector, value = target_to_selector_value(target_pair)
                self.find_element(selector, value).send_keys(command.value)
                events.append(SeleniumScriptLogEvent(message=f'Typed `{command.value}` into `{target_pair}`'))
            except Exception as e:
                message = f'Failed to execute type `{command.id}`.`{target_pair}`'
                events.append(SeleniumScriptErrorEvent(message=message, from_exception=str(e)))
                exception = SeleniumCommandException(message, base_exception=e)

        return events, exception

    def mouse_over(self, command: SeleniumCommand) -> tuple[list[Event], SeleniumCommandException | None]:
        events: list[Event] = []
        exception: SeleniumCommandException | None = None

        for target_pair in command.targets:
            try:
                selector, value = target_to_selector_value(target_pair)
                ActionChains(self.driver).move_to_element(  # type: ignore[no-untyped-call]
                    self.find_element(selector, value),
                ).perform()
                events.append(SeleniumScriptLogEvent(message=f'Moved mouse over `{target_pair}`'))
            except Exception as e:
                message = f'Failed to execute mouseOver `{command.id}`.`{target_pair}`'
                events.append(SeleniumScriptErrorEvent(message=message, from_exception=str(e)))
                exception = SeleniumCommandException(message, base_exception=e)

        return events, exception

    def mouse_out(self, command: SeleniumCommand) -> tuple[list[Event], SeleniumCommandException | None]:
        events: list[Event] = []
        exception: SeleniumCommandException | None = None

        for target_pair in command.targets:
            try:
                selector, value = target_to_selector_value(target_pair)

                ActionChains(self.driver).move_to_element(  # type: ignore[no-untyped-call]
                    self.find_element(selector, value),
                ).perform()
                events.append(SeleniumScriptLogEvent(message=f'Moved mouse out of `{target_pair}`'))
            except Exception as e:
                message = f'Failed to execute mouseOut `{command.id}`.`{target_pair}`'
                events.append(SeleniumScriptErrorEvent(message=message, from_exception=str(e)))
                exception = SeleniumCommandException(message, base_exception=e)

        return events, exception

    def wait(self, command: SeleniumCommand) -> tuple[list[Event], SeleniumCommandException | None]:
        events: list[Event] = []
        exception: SeleniumCommandException | None = None

        if command.target:
            cmd, value = command.target.split('=')
            if cmd == 'request_url_contains':
                wait_events, exception = self.wait_for_request_url_contains(value)
                events.extend(wait_events)
            return events, exception

        time.sleep(int(command.value))
        events.append(SeleniumScriptLogEvent(message=f'Waited for {command.value} seconds'))
        return events, None

    def wait_for_request_url_contains(self, regex: str) -> tuple[list[Event], SeleniumCommandException | None]:
        events: list[Event] = []

        started_at = time.time()
        while started_at + self.wait_for_seconds > time.time():
            for request in self.driver.requests:
                if re.match(regex, request.url):
                    events.append(SeleniumScriptLogEvent(message=f'Found request url {request.url} matching `{regex}`'))
                    return events, None

            time.sleep(self.pooling_interval)

        events.append(
            SeleniumScriptLogEvent(message=f'Failed to find request url matching `{regex}`', severity='warning'),
        )
        return events, None
