import logging
import re
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver  # type: ignore[import]

from multiauth.providers.webdriver.core import SeleniumCommand
from multiauth.providers.webdriver.transformers import target_to_selector_value


class SeleniumCommandHandler:
    driver: webdriver.Firefox
    logger: logging.Logger

    wait_for_seconds: int
    pooling_interval: float

    def __init__(self, driver: webdriver.Firefox) -> None:
        self.driver = driver
        self.logger = logging.getLogger('multiauth.providers.webdriver.seleniumcommandhandler')
        self.wait_for_seconds = 30
        self.pooling_interval = 0.5

    def find_element(self, selector, value) -> WebElement:
        wait = WebDriverWait(self.driver, self.wait_for_seconds)
        return wait.until(EC.presence_of_element_located((selector, value)))

    def open(self, command: SeleniumCommand) -> None:
        self.driver.get(command.target)

    def set_window_size(self, command: SeleniumCommand) -> None:
        width, height = command.target.split('x')
        self.driver.set_window_size(int(width), int(height))

    def click(self, command: SeleniumCommand, retries: int | None = None) -> None:
        last_exc = None
        for target_pair in command.targets:
            try:
                selector, value = target_to_selector_value(target_pair)
                return self.find_element(selector, value).click()
            except Exception as e:
                logging.info(
                    'Failed to execute click `%s`.`%s`: %s',
                    command.id,
                    target_pair,
                    e,
                )
                last_exc = e

        if retries is None:
            self.logger.info('Retrying click `%s`', command.id)
            self.driver.implicitly_wait(10)
            return self.click(command, retries=1)

        if last_exc:
            raise last_exc

    def type(self, command: SeleniumCommand) -> None:
        last_exc = None
        for target_pair in command.targets:
            try:
                selector, value = target_to_selector_value(target_pair)
                return self.find_element(selector, value).send_keys(command.value)
            except Exception as e:
                logging.info(
                    'Failed to execute type `%s`.`%s`: %s',
                    command.id,
                    target_pair,
                    e,
                )
                last_exc = e

        if last_exc:
            raise last_exc

    def mouse_over(self, command: SeleniumCommand) -> None:
        last_exc = None
        for target_pair in command.targets:
            try:
                selector, value = target_to_selector_value(target_pair)
                return ActionChains(self.driver).move_to_element(
                    self.find_element(selector, value)
                ).perform()
            except Exception as e:
                logging.info(
                    'Failed to execute mouesOver `%s`.`%s`: %s',
                    command.id,
                    target_pair,
                    e,
                )
                last_exc = e

        if last_exc:
            raise last_exc

    def mouse_out(self, command: SeleniumCommand) -> None:
        last_exc = None
        for target_pair in command.targets:
            try:
                selector, value = target_to_selector_value(target_pair)
                return ActionChains(self.driver).move_to_element(
                    self.find_element(selector,value)
                ).perform()
            except Exception as e:
                logging.info(
                    'Failed to execute mouseOut `%s`.`%s`: %s',
                    command.id,
                    target_pair,
                    e,
                )
                last_exc = e

        if last_exc:
            raise last_exc

    def wait(self, command: SeleniumCommand) -> None:
        if command.target:
            cmd, value = command.target.split('=')
            if cmd == 'request_url_contains':
                return self.wait_for_request_url_contains(value)

        else:
            time.sleep(int(command.value))

    def wait_for_request_url_contains(self, regex: str) -> None:
        started_at = time.time()
        while started_at + self.wait_for_seconds > time.time():
            for request in self.driver.requests:
                if re.match(regex, request.url):
                    return

            time.sleep(self.pooling_interval)
