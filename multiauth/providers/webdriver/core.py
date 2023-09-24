from multiauth.entities.providers.webdriver import SeleniumCommand, SeleniumProject, SeleniumTest


def load_selenium_project(data: dict) -> 'SeleniumProject':
    return SeleniumProject(
        # id=data['id'],
        # version=data['version'],
        # name=data['name'],
        # url=data['url'],
        tests=[
            SeleniumTest(
                id=test['id'],
                name=test['name'],
                commands=[
                    SeleniumCommand(
                        id=command['id'],
                        # comment=command['comment'],
                        command=command['command'],
                        target=command['target'],
                        targets=command['targets'],
                        value=command['value'],
                    )
                    for command in test['commands']
                ],
            )
            for test in data['tests']
        ],
    )
