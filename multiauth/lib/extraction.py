from pydantic import BaseModel, Field

from multiauth.lib.http_core.entities import HTTPLocation
from multiauth.lib.store.variables import VariableName


class TokenExtraction(BaseModel):
    location: HTTPLocation = Field(description='The location of the HTTP request where the value should be extracted')
    key: str = Field(description='The key to use for the extracted value, depending on the location')
    regex: str | None = Field(
        description='The regex to use to extract the token from the key value. By default the entire value is taken.',
        default=None,
    )
    name: VariableName = Field(
        description='The name of the variable to store the extracted value into',
        examples=['my-token'],
    )

    @staticmethod
    def examples() -> list:
        return [
            TokenExtraction(key='Set-Cookie', location=HTTPLocation.HEADER, name=VariableName('my-variable')).dict(
                exclude_defaults=True,
            ),
        ]
