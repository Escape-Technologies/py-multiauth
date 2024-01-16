from pydantic import Field

from multiauth.helpers.base_model import StrictBaseModel
from multiauth.lib.entities import VariableName


class AuthenticationVariable(StrictBaseModel):
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
