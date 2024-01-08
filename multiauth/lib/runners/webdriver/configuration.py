from pydantic import BaseModel


class SeleniumCommand(BaseModel):
    id: str
    # comment: str
    command: str
    target: str
    targets: list[list[str]]
    value: str


class SeleniumTest(BaseModel):
    id: str
    name: str
    commands: list[SeleniumCommand]


class SeleniumProject(BaseModel):
    # id: str
    # version: str
    # name: str
    # url: str
    tests: list[SeleniumTest]
