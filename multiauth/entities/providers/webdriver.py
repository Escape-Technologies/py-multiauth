from dataclasses import dataclass


@dataclass
class SeleniumCommand:
    id: str
    # comment: str
    command: str
    target: str
    targets: list[list[str]]
    value: str


@dataclass
class SeleniumTest:
    id: str
    name: str
    commands: list[SeleniumCommand]


@dataclass
class SeleniumProject:
    # id: str
    # version: str
    # name: str
    # url: str
    tests: list[SeleniumTest]
