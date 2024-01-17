from uuid import uuid4

from pydantic import BaseModel, Field

from multiauth.helpers.base_model import StrictBaseModel


class SeleniumCommand(BaseModel):
    id: str
    command: str = Field(
        description=('The command of the test.'),
        examples=['open'],
    )
    target: str = Field(
        description=('The target of the test.'),
        examples=['https://example.com'],
    )
    targets: list[list[str]] = Field(
        description=('The targets of the test.'),
        examples=[['css', 'body']],
    )
    value: str = Field(
        description=('The value of the test.'),
        examples=['some-value'],
    )

    @staticmethod
    def examples() -> list:
        return [
            SeleniumCommand(
                id=uuid4().hex,
                command='open',
                target='https://example.com',
                targets=[['css', 'body']],
                value='',
            ).dict(exclude_defaults=True),
        ]


class SeleniumTest(StrictBaseModel):
    id: str = Field(
        description=('The id of the test.'),
        examples=[uuid4().hex],
    )
    name: str = Field(
        description=('The name of the test.'),
        examples=['my-test'],
    )
    commands: list[SeleniumCommand] = Field(
        description=('The commands of the test.'),
        examples=SeleniumCommand.examples(),
    )

    @staticmethod
    def examples() -> list:
        return [
            SeleniumTest(
                id=uuid4().hex,
                name='test',
                commands=[
                    SeleniumCommand(
                        id=uuid4().hex,
                        targets=[['css', 'body']],
                        value='',
                        command='open',
                        target='https://example.com',
                    ),
                ],
            ).dict(exclude_defaults=True),
        ]


class SeleniumProject(BaseModel):
    # id: str | None = Field(default=None, description='The uuid of the Selenium project.')
    # version: str | None = Field(default=None, description='The version of the Selenium project.')
    # name: str | None = Field(default=None, description='The name of the Selenium project.')
    # urls: list | None = Field(default=None, description='The urls of the Selenium project.')
    # suites: list | None = Field(default=None, description='The suites of the Selenium project.')
    # plugins: list | None = Field(default=None, description='The plugins of the Selenium project.')

    tests: list[SeleniumTest] = Field(
        description=('The tests of the Selenium script.'),
        examples=SeleniumTest.examples(),
    )

    @staticmethod
    def examples() -> list:
        return [
            SeleniumProject(
                tests=[
                    SeleniumTest(
                        id='test',
                        name='test',
                        commands=[
                            SeleniumCommand(
                                id='command',
                                targets=[['css', 'body']],
                                value='',
                                command='open',
                                target='https://example.com',
                            ),
                        ],
                    ),
                ],
            ),
        ]
