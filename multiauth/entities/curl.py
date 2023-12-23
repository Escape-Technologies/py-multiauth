"""Custom data used in utils."""


from http import HTTPMethod

from pydantic import BaseModel


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
