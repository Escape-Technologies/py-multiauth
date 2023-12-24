from pydantic import Field

from multiauth.new.entities.main import AuthProvider, Credentials


class BasicCredentials(Credentials):
    username: str = Field(description='The Basic username of the user.')
    password: str = Field(description='The Basic password of the user.')


class BasicAuthProvider(AuthProvider):
    pass
