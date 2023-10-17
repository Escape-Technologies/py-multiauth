from multiauth.entities.providers.webdriver import SeleniumCommand, SeleniumProject, SeleniumTest


def load_selenium_project(data: dict) -> 'SeleniumProject':
    return SeleniumProject(
        # id=data['id'],
        # version=data['version'],
        # name=data['name'],
        # url=data['url'],
        tests=load_selenium_tests(data),
    )


def load_selenium_tests(data: dict) -> list[SeleniumTest]:
    return [load_selenium_test(test) for test in data['tests']]


def load_selenium_test(test: dict) -> SeleniumTest:
    return SeleniumTest(
        id=test['id'],
        name=test['name'],
        commands=load_selenium_commands(test),
    )


def load_selenium_commands(test: dict) -> list[SeleniumCommand]:
    return [load_selenium_command(command) for command in test['commands']]


def load_selenium_command(command: dict) -> SeleniumCommand:
    return SeleniumCommand(
        id=command['id'],
        # comment=command['comment'],
        command=command['command'],
        target=command['target'],
        targets=command['targets'],
        value=command['value'],
    )
