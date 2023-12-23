from multiauth.new.entities.main import Credentials


class OAuth2AuthCodeCredentials(Credentials):
    clientId: str
    clientSecret: str


class OAuth2ClientCredentials(Credentials):
    clientId: str
    clientSecret: str


class OAuth2PasswordCredentials(Credentials):
    clientId: str
    clientSecret: str
    username: str
    password: str


class OAuth2ImplicitCredentials(Credentials):
    clientId: str
