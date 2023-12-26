from pydantic import BaseModel


class AuthenticationVariable(BaseModel):
    name: str
    value: str


def interpolate_string(string: str, variables: list[AuthenticationVariable]) -> str:
    """Interpolate a string with variables."""

    for variable in variables:
        string = string.replace('{{ %s }}' % variable.name, variable.value)
        string = string.replace('{{ %s}}' % variable.name, variable.value)
        string = string.replace('{{%s }}' % variable.name, variable.value)
        string = string.replace('{{%s}}' % variable.name, variable.value)

    return string
