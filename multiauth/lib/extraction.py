from pydantic import Field

from multiauth.helpers.base_model import StrictBaseModel
from multiauth.lib.http_core.entities import HTTPLocation
from multiauth.lib.presets.base import generate_seeded_slug
from multiauth.lib.store.variables import VariableName


class TokenExtraction(StrictBaseModel):
    location: HTTPLocation = Field(description='The location of the HTTP request where the value should be extracted')
    key: str = Field(description='The key to use for the extracted value, depending on the location')
    regex: str | None = Field(
        description='The regex to use to extract the token from the key value. By default the entire value is taken.',
        default=None,
    )
    name: VariableName | None = Field(
        default=None,
        description='The name of the variable to store the extracted value into',
        examples=['my-token'],
    )

    @property
    def slug(self) -> VariableName:
        return self.name or VariableName(generate_seeded_slug(f'{self.location.value}:{self.key}:{self.regex}'))

    @staticmethod
    def examples() -> list:
        return [
            TokenExtraction(key='Set-Cookie', location=HTTPLocation.HEADER, name=VariableName('my-variable')).dict(
                exclude_defaults=True,
            ),
        ]
