import logging
import os
from types import TracebackType
from typing import Any, Self

from selenium.webdriver import firefox
from seleniumwire import webdriver  # type: ignore[import-untyped]

from multiauth.entities.errors import AuthenticationError
from multiauth.providers.webdriver.command import SeleniumCommandHandler
from multiauth.providers.webdriver.core import SeleniumTest


class SeleniumTestRunner:
    driver: webdriver.Firefox | None
    logger: logging.Logger
    proxy: str | None

    def __init__(self, proxy: str | None = None) -> None:
        self.driver = None
        self.logger = logging.getLogger('multiauth.providers.webdriver.seleniumtestrunner')
        self.proxy = proxy

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self.driver:
            self.driver.quit()
            self.driver = None

    def run(self, test: SeleniumTest) -> Any:
        self.logger.info('Setting up driver..')
        self.driver = self.setup_driver()
        self.logger.info('Initialized firefox browser..')

        hdlr = SeleniumCommandHandler(self.driver)
        cmd_mapping: dict = {
            'open': hdlr.open,
            'setWindowSize': hdlr.set_window_size,
            'click': hdlr.click,
            'type': hdlr.type,
            'mouseOver': hdlr.mouse_over,
            'mouseOut': hdlr.mouse_out,
            'wait': hdlr.wait,
            'selectFrame': hdlr.select_frame,
        }

        for command in test.commands:
            self.logger.info('Executing command: %s (%s)', command.command, command.id)

            if command.command == 'close':
                break

            if command.command not in cmd_mapping:
                raise AuthenticationError(f'Invalid command `{command.command}` (`{command.id}`)')

            try:
                cmd_mapping[command.command](command)
            except Exception as e:
                # self.driver.save_screenshot(f'{command.id}.png')
                raise AuthenticationError(f'Failed to execute command `{command} (`{command.id}`)') from e

        return self.driver.requests

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

        if self.proxy:
            driver.proxy = {'http': self.proxy, 'https': self.proxy}

        self.logger.info('Prepared firefox profile..')

        return driver
