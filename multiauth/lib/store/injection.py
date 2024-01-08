from pydantic import BaseModel, Field

from multiauth.lib.http_core.entities import HTTPLocation


class TokenInjection(BaseModel):
    location: HTTPLocation = Field(description='The location of the HTTP request where the token should be injected')
    key: str = Field(
        description=(
            'The key to use for the injected token. Its usage depends on the location. For headers, cookies,'
            'and query parameters, this key describes the name of the header, cookie or query parameter. For a body '
            'location, the key is the field where the token should be injected within the request bodies'
        ),
        examples=['Authorization', 'sessionId', 'access_token'],
    )
    prefix: str | None = Field(
        default=None,
        description='A prefix to prepend to the token before it is injected',
        examples=['Bearer '],
    )
    variable: str | None = Field(
        default=None,
        description=(
            "The name of a variable to retrieve to create the token's value. If not provided, "
            'the token will be infered as the first successful extraction of the procedure'
        ),
    )
