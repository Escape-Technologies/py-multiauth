from dataclasses import dataclass

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


@dataclass
class WebdriverConfig(BaseModel):

    """Authentication Configuration Parameters of the Webdriver Method."""

    extract_location: str
    extract_regex: str
    project: SeleniumProject
    output_format: str
    token_lifetime: int | None
    extract_match_index: int | None
