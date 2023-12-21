"""Custom data used in utils."""


from pydantic import BaseModel

from multiauth.entities.http import HTTPMethod


class RawCredentials(BaseModel):

    """This is the credentials class that are the credentials found in the curl."""

    username: str
    password: str


class ParsedCurlContent(BaseModel):

    """This is the datatype which shows the curl command."""

    method: HTTPMethod
    url: str
    data: str | None
    headers: dict[str, str]
    credentials: RawCredentials | None
