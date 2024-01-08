import os

from selenium.webdriver import firefox
from seleniumwire import webdriver  # type: ignore[import-untyped]

from multiauth.lib.runners.webdriver.runner import SeleniumScriptOptions


def setup_driver(options: SeleniumScriptOptions) -> webdriver.Firefox:
    firefox_options = firefox.options.Options()
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--headless')
    firefox_options.add_argument('--disable-gpu')
    firefox_options.set_preference('browser.download.folderList', 2)
    firefox_options.set_preference('browser.download.manager.showWhenStarting', False)
    firefox_options.set_preference('browser.download.dir', os.getcwd())
    firefox_options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

    driver = webdriver.Firefox(options=firefox_options)

    if options.proxy:
        driver.proxy = {'http': options.proxy, 'https': options.proxy}

    return driver
