import logging
import time
from datetime import timedelta

import pkg_resources

from multiauth.entities.errors import AuthenticationError
from multiauth.entities.main import AuthResponse, AuthTech, WebdriverConfig
from multiauth.manager import User
from multiauth.providers.webdriver.core import load_selenium_project
from multiauth.providers.webdriver.extractors import extract_token
from multiauth.providers.webdriver.runner import SeleniumTestRunner

logger = logging.getLogger('multiauth.providers.webdriver')


__version__ = pkg_resources.get_distribution('py-multiauth').version



def webdriver_config_parser(schema: dict) -> WebdriverConfig:
    if not schema.get('extract_location'):
        raise AuthenticationError('Please provide the location to where you want to extract the token')

    if not schema.get('extract_regex'):
        raise AuthenticationError('Please provide the regex to extract the token')

    if not schema.get('project'):
        raise AuthenticationError('Please provide the project to run the webdriver tests')

    if not schema.get('project').get('tests'):
        raise AuthenticationError('Please provide the tests to run the webdriver tests')

    options = schema.get('options') or {}

    auth_config = WebdriverConfig(
        extract_location=schema['extract_location'],
        extract_regex=schema['extract_regex'],
        project=load_selenium_project(schema['project']),
        output_format=options.get('output_format'),
        token_lifetime=options.get('token_lifetime'),
        extract_match_index=options.get('extract_match_index'),
    )

    if auth_config.output_format:
        if '@token@' not in auth_config.output_format:
            raise AuthenticationError('Please provide the token placeholder in the output format (`@token`).')
    else:
        auth_config.output_format = 'Authorization: Bearer @token@'

    if len(auth_config.project.tests) > 1:
        logger.warning(f'Found {len(auth_config.project.tests)}, only the first one will be executed')

    return auth_config


def webdriver_authenticator(user: User, schema: dict) -> AuthResponse:
    auth_config = webdriver_config_parser(schema)

    selenium_test = auth_config.project.tests[0]
    logger.info(f'Webdriver authentication using Multiauth {__version__}')
    logger.info(f'Executing test: {selenium_test.name}')

    with SeleniumTestRunner() as r:
        requests: list = r.run(selenium_test)

    logger.info(f'Finished executing Selenium test. Sent `{len(requests)}` requests')

    token = extract_token(
        auth_config.extract_location,
        auth_config.extract_regex,
        auth_config.extract_match_index,
        requests,
    )
    logger.info('Extracted token')

    formatted_token = auth_config.output_format.replace('@token@', token)
    splitted = formatted_token.split(':')
    header_key = splitted[0].strip()
    header_value = ':'.join(splitted[1:]).strip()
    logger.info(f'Formatted header: {header_key}')

    if auth_config.token_lifetime:
        user.expires_in = time.time() + timedelta(seconds=auth_config.token_lifetime).total_seconds()

    return AuthResponse(
        tech=AuthTech.WEBDRIVER,
        headers={
            header_key: header_value,
        },
    )
