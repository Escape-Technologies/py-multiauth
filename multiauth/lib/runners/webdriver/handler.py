import logging
import re
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver  # type: ignore[import-untyped]
from seleniumwire.request import Request  # type: ignore[import-untyped]

from multiauth.lib.audit.events.base import EventsList
from multiauth.lib.audit.events.events import (
    HTTPFailureEvent,
    HTTPRequestEvent,
    HTTPResponseEvent,
    SeleniumScriptErrorEvent,
    SeleniumScriptLogEvent,
)
from multiauth.lib.http_core.entities import HTTPHeader, HTTPQueryParameter, HTTPRequest, HTTPResponse
from multiauth.lib.runners.base import RunnerException
from multiauth.lib.runners.webdriver.configuration import SeleniumCommand
from multiauth.lib.runners.webdriver.transformers import (
    target_to_selector_value,
    target_to_value,
)


class SeleniumCommandException(RunnerException):
    base_exception: Exception | None

    def __init__(self, message: str, base_exception: Exception | None = None) -> None:
        self.base_exception = base_exception
        super().__init__(message)


def build_http_request_from_selenium_request(request: Request) -> HTTPRequest:
    return HTTPRequest(
        method=request.method.upper(),
        cookies=[],
        data_text=request.body.decode('utf-8', 'ignore') if request.body else '',
        headers=[HTTPHeader(name=name, values=[str(value)]) for name, value in request.headers.items()],
        host=request.host,
        path=request.path,
        scheme=request.url.split('://')[0],
        query_parameters=[
            HTTPQueryParameter(
                name=name,
                values=values if isinstance(values, list) else [values],
            )
            for name, values in request.params.items()
        ],
    )


def build_http_response_from_selenium_request(request: Request) -> HTTPResponse:
    return HTTPResponse(
        status_code=request.response.status_code,
        data_text=request.response.body.decode('utf-8', 'ignore') if request.response.body else '',
        headers=[HTTPHeader(name=name, values=[str(value)]) for name, value in request.response.headers.items()],
        reason=request.response.reason,
        elapsed=(request.response.date - request.date).total_seconds(),
        url=request.url,
        cookies=[],
    )


logger = logging.getLogger(__name__)


class SeleniumCommandHandler:
    driver: webdriver.Firefox

    wait_for_seconds: int
    pooling_interval: float

    reported_hosts: set[str]

    def __init__(
        self,
        driver: webdriver.Firefox,
        wait_for_seconds: int = 5,
        reported_hosts: set[str] | None = None,
    ) -> None:
        self.driver = driver
        self.wait_for_seconds = wait_for_seconds
        self.pooling_interval = 0.5
        self.reported_hosts = reported_hosts or set()

    def get_http_events_from(
        self,
        from_index: int = 0,
    ) -> list[HTTPRequestEvent | HTTPFailureEvent | HTTPResponseEvent]:
        events: list[HTTPRequestEvent | HTTPFailureEvent | HTTPResponseEvent] = []

        blacklisted_extensions = [
            '.js',
            '.css',
            '.png',
            '.jpg',
            '.gif',
            '.json',
            '.ico',
            '.svg',
            '.woff',
            '.woff2',
            '.eot',
            '.ttf',
            '.otf',
        ]

        requests: list[Request] = [
            r
            for r in self.driver.requests[from_index:]
            if not any(r.url.endswith(ext) for ext in blacklisted_extensions)
        ]

        for request in requests:
            if next((host for host in self.reported_hosts if host in request.url), None) is None:
                continue
            try:
                events.append(
                    HTTPRequestEvent(
                        request=build_http_request_from_selenium_request(request),
                    ),
                )

                if request.response:
                    events.append(
                        HTTPResponseEvent(
                            response=build_http_response_from_selenium_request(request),
                        ),
                    )
                else:
                    events.append(
                        HTTPFailureEvent(
                            reason='unknown',
                            description='No response received',
                        ),
                    )
            except Exception as e:
                logger.error(f'Failed to build HTTP request from selenium request: {e}')
                events.append(
                    HTTPFailureEvent(
                        reason='unknown',
                        description=f'Failed to decode response: {e}',
                    ),
                )
                continue

        return events

    def run_command(self, command: SeleniumCommand) -> tuple[EventsList, SeleniumCommandException | None]:
        current_request_index = len(self.driver.requests)
        match command.command:
            case 'open':
                events, exception = self.open(command)
            case 'setWindowSize':
                events, exception = self.set_window_size(command)
            case 'click':
                events, exception = self.click(command)
            case 'type':
                events, exception = self.type(command)
            case 'mouseOver':
                events, exception = self.mouse_over(command)
            case 'mouseOut':
                events, exception = self.mouse_out(command)
            case 'wait':
                events, exception = self.wait(command)
            case 'selectFrame':
                events, exception = self.select_frame(command)
            case _:
                message = f'Unhandled command `{command.command}`'
                error = SeleniumCommandException(message=message)
                events = EventsList(SeleniumScriptErrorEvent(message=message, from_exception=str(error)))
                return events, error

        events.extend(self.get_http_events_from(current_request_index))

        return events, exception

    def find_element(self, selector: str, value: str) -> WebElement:
        wait = WebDriverWait(self.driver, self.wait_for_seconds)
        return wait.until(EC.presence_of_element_located((selector, value)))

    def safe_click(self, selector: str, value: str) -> tuple[EventsList, SeleniumCommandException | None]:
        tries = 0
        events = EventsList()
        for _ in range(2):
            try:
                tries += 1
                events.append(
                    SeleniumScriptLogEvent(
                        message=f'Clicking on element with selector `{selector}` and value `{value}`',
                    ),
                )
                self.find_element(selector, value).click()
                events.append(
                    SeleniumScriptLogEvent(
                        message=(
                            f'Clicked on element with selector `{selector}` and value `{value}` after {tries} tries'
                        ),
                    ),
                )
                return events, None
            except Exception as e:
                events.append(
                    SeleniumScriptErrorEvent(
                        message=f'Failed to click on element with `{selector}` and value `{value}` after {tries} tries',
                    ),
                )
                time.sleep(1)
                last_error = e

        error_message = f'Failed to click on element `{selector}` after {tries} tries'
        events.append(SeleniumScriptErrorEvent(severity='error', message=error_message, from_exception=str(last_error)))
        return events, SeleniumCommandException(error_message, base_exception=last_error)

    def safe_switch_to_frame(self, selector: int | str) -> tuple[EventsList, SeleniumCommandException | None]:
        tries = 0
        events = EventsList()
        for _ in range(2):
            try:
                tries += 1
                events.append(SeleniumScriptLogEvent(message=f'Switching to frame with selector `{selector}`'))
                self.driver.switch_to.frame(selector)
                events.append(
                    SeleniumScriptLogEvent(severity='info', message=f'Switched to frame with selector `{selector}`'),
                )
                return events, None
            except Exception as e:
                time.sleep(1)
                events.append(
                    SeleniumScriptLogEvent(
                        severity='warning',
                        message=f'Failed to switch to frame with selector `{selector}`, retrying...',
                    ),
                )
                last_error = e

        message = f'Failed to switch to frame with `{selector}` after {tries} retries'
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

    def open(self, command: SeleniumCommand) -> tuple[EventsList, SeleniumCommandException | None]:
        events = EventsList()
        url = command.target

        try:
            self.driver.get(url)
            events.append(SeleniumScriptLogEvent(message=f'Opened URL `{url}`'))
            return events, None
        except Exception as e:
            events.append(SeleniumScriptErrorEvent(message=f'Failed to open URL `{url}`', from_exception=str(e)))
            return events, SeleniumCommandException(f'Failed to open URL `{url}`: {e}', base_exception=e)

    def set_window_size(self, command: SeleniumCommand) -> tuple[EventsList, SeleniumCommandException | None]:
        events = EventsList()

        width, height = command.target.split('x')

        try:
            logger.info(f'Set window size to {width}x{height}')
            self.driver.set_window_size(int(width), int(height))
            logger.info(f'Done setting window size to {width}x{height}')
            events.append(SeleniumScriptLogEvent(message=f'Set window size to `{width}x{height}`'))
            return events, None
        except Exception as e:
            logger.error(f'Failed to set window size to {width}x{height}: {e}')
            message = f'Failed to set window size to `{width}x{height}`'
            events.append(SeleniumScriptErrorEvent(message=message, from_exception=str(e)))
            return events, SeleniumCommandException(message, base_exception=e)

    def click(
        self,
        command: SeleniumCommand,
        retries: int | None = None,
    ) -> tuple[EventsList, SeleniumCommandException | None]:
        events = EventsList()

        for target_pair in command.targets:
            try:
                selector, value = target_to_selector_value(target_pair)
                click_events, exception = self.safe_click(selector, value)
                events.extend(click_events)
                if exception is None:
                    return events, None
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

    def select_frame(self, command: SeleniumCommand) -> tuple[EventsList, SeleniumCommandException | None]:
        events = EventsList()
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
            events.append(SeleniumScriptErrorEvent(message=message, from_exception=str(e)))
            exception = SeleniumCommandException(message=message, base_exception=e)

        return events, exception

    def type(self, command: SeleniumCommand) -> tuple[EventsList, SeleniumCommandException | None]:
        events = EventsList()
        exception: SeleniumCommandException | None = None

        for target_pair in command.targets:
            try:
                selector, value = target_to_selector_value(target_pair)
                self.find_element(selector, value).send_keys(command.value)
                events.append(SeleniumScriptLogEvent(message=f'Typed `{command.value}` into `{target_pair}`'))
                return events, None
            except Exception as e:
                message = f'Failed to execute type `{command.id}`.`{target_pair}`'
                events.append(SeleniumScriptErrorEvent(message=message, from_exception=str(e)))
                exception = SeleniumCommandException(message, base_exception=e)

        return events, exception

    def mouse_over(self, command: SeleniumCommand) -> tuple[EventsList, SeleniumCommandException | None]:
        events = EventsList()
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

    def mouse_out(self, command: SeleniumCommand) -> tuple[EventsList, SeleniumCommandException | None]:
        events = EventsList()
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

    def wait(self, command: SeleniumCommand) -> tuple[EventsList, SeleniumCommandException | None]:
        events = EventsList()
        exception: SeleniumCommandException | None = None

        try:
            max_wait_time = int(command.value)
        except ValueError:
            events.append(
                SeleniumScriptErrorEvent(
                    message=f'Invalid wait value `{command.value}`, fall back to {self.wait_for_seconds}',
                ),
            )
            max_wait_time = self.wait_for_seconds

        if command.target:
            cmd, value = command.target.split('=')
            if cmd == 'request_url_contains':
                wait_events, exception = self.wait_for_request_url_contains(value, max_wait_time)
                events.extend(wait_events)
            return events, exception

        time.sleep(max_wait_time)
        events.append(SeleniumScriptLogEvent(message=f'Waited for {max_wait_time} seconds'))
        return events, None

    def wait_for_request_url_contains(
        self,
        regex: str,
        max_wait_time: int,
    ) -> tuple[EventsList, SeleniumCommandException | None]:
        events = EventsList()

        started_at = time.time()
        while started_at + max_wait_time > time.time():
            for request in self.driver.requests:
                if re.search(regex, request.url):
                    events.append(SeleniumScriptLogEvent(message=f'Found request url {request.url} matching `{regex}`'))
                    return events, None

            time.sleep(self.pooling_interval)

        events.append(
            SeleniumScriptLogEvent(
                message=f'Failed to find request url matching `{regex}` after waiting {max_wait_time}s',
                severity='warning',
            ),
        )
        return events, None
