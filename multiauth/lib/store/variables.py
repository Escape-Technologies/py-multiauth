from typing import NewType

from pydantic import BaseModel, Field

VariableName = NewType('VariableName', str)


class AuthenticationVariable(BaseModel):
    name: VariableName = Field(description='The name of the variable')
    value: str = Field(description='The value of the variable')


def interpolate_string(string: str, variables: list[AuthenticationVariable]) -> str:
    """Interpolate a string with variables."""

    for variable in variables:
        string = string.replace('{{ %s }}' % variable.name, variable.value)
        string = string.replace('{{ %s}}' % variable.name, variable.value)
        string = string.replace('{{%s }}' % variable.name, variable.value)
        string = string.replace('{{%s}}' % variable.name, variable.value)

    return string
