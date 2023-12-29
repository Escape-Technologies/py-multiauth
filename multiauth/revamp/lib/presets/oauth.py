from pydantic import Field

from multiauth.entities.providers.oauth import AuthOAuthClientMethod
from multiauth.entities.providers.webdriver import SeleniumCommand
from multiauth.revamp.lib.presets.main import AuthProvider, AuthRequester, Credentials

###########################
###### TODO(maxence@escape.tech, antoine@escape.tech): We should stop doing that a
# nd use this method: https://backstage.forgerock.com/knowledge/kb/article/a45882528
###########################


###########################
#### OAuth2 Auth Code #####
###########################


class OAuth2AuthCodeCredentials(Credentials):
    clientId: str
    clientSecret: str


class OAuth2AuthCodeAuthRequester(AuthRequester):
    url: str = Field(description='The URL to request the authorization code')
    tokenUrl: str = Field(description='The URL to exchange the authorization code for an access token')
    redirectUrl: str = Field(description='The URL to redirect to after authorization')
    clientMethod: AuthOAuthClientMethod = Field(
        default=AuthOAuthClientMethod.BASIC,
        description='The client authentication method for token endpoint.',
    )
    webDriverCommmands: list[SeleniumCommand] = Field(description='The commands to execute in the web driver')
    scope: str | None = Field(default=None, description='The scope to request access to')
    state: str | None = Field(default=None, description='The state is used to prevent CSRF attacks')
    codeVerifier: str | None = Field(default=None, description='The code verifier used to generate the code challenge')


class OAuth2AuthCodeAuthProvider(AuthProvider):
    """This OAuth2 flow requires a Webdriver."""

    requester: OAuth2AuthCodeAuthRequester


###########################
###### OAuth2 Client ######
###########################
class OAuth2ClientCredentials(Credentials):
    clientId: str
    clientSecret: str


class OAuth2ClientAuthRequester(AuthRequester):
    url: str = Field(description='The URL to request the authorization code')
    tokenUrl: str = Field(description='The URL to exchange the authorization code for an access token')
    scope: str | None = Field(default=None, description='The scope to request access to')


class OAuth2ClientAuthProvider(AuthProvider):
    requester: OAuth2ClientAuthRequester


###########################
##### OAuth2 Password #####
###########################


class OAuth2PasswordCredentials(Credentials):
    clientId: str
    clientSecret: str
    username: str
    password: str


class OAuth2PasswordAuthRequester(AuthRequester):
    url: str = Field(description='The URL to request the authorization code')
    tokenUrl: str = Field(description='The URL to exchange the authorization code for an access token')
    clientMethod: AuthOAuthClientMethod = Field(
        default=AuthOAuthClientMethod.BASIC,
        description='The client authentication method for token endpoint.',
    )
    scope: str | None = Field(default=None, description='The scope to request access to')


class OAuth2PasswordAuthProvider(AuthProvider):
    requester: OAuth2PasswordAuthRequester


###########################
##### OAuth2 Implicit #####
###########################


class OAuth2ImplicitCredentials(Credentials):
    clientId: str


class OAuth2ImplicitAuthRequester(AuthRequester):
    url: str = Field(description='The URL to request the authorization code')
    redirectUrl: str = Field(description='The URL to redirect to after authorization')
    webDriverCommmands: list[SeleniumCommand] = Field(description='The commands to execute in the web driver')
    clientMethod: AuthOAuthClientMethod = Field(
        default=AuthOAuthClientMethod.BASIC,
        description='The client authentication method for token endpoint.',
    )
    scope: str | None = Field(default=None, description='The scope to request access to')
    state: str | None = Field(default=None, description='The state is used to prevent CSRF attacks')


class OAuth2ImplicitAuthProvider(AuthProvider):
    """This OAuth2 flow requires a Webdriver."""

    requester: OAuth2ImplicitAuthRequester


###########################
###### OAuth2 Refresh #####
###########################


class OAuth2RefreshCredentials(Credentials):
    refreshToken: str


class OAuth2RefreshProvider(AuthProvider):
    pass
