from enum import StrEnum

from pydantic import Field

from multiauth.lib.presets.base_old import AuthPreset, RequestPreset, UserPreset
from multiauth.lib.runners.webdriver.configuration import SeleniumCommand

###########################
###### TODO(maxence@escape.tech, antoine@escape.tech): We should stop doing that a
# nd use this method: https://backstage.forgerock.com/knowledge/kb/article/a45882528
###########################


###########################
#### OAuth2 Auth Code #####
###########################


class AuthOAuthClientMethod(StrEnum):
    BASIC = 'basic'
    POST = 'post'


class OAuth2AuthCodeUserPreset(UserPreset):
    clientId: str
    clientSecret: str


class OAuth2AuthCodeRequestPreset(RequestPreset):
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


class OAuth2AuthCodeAuthPreset(AuthPreset):
    """This OAuth2 flow requires a Webdriver."""

    request: OAuth2AuthCodeRequestPreset


###########################
###### OAuth2 Client ######
###########################
class OAuth2ClientUserPreset(UserPreset):
    clientId: str
    clientSecret: str


class OAuth2ClientRequestPreset(RequestPreset):
    url: str = Field(description='The URL to request the authorization code')
    tokenUrl: str = Field(description='The URL to exchange the authorization code for an access token')
    scope: str | None = Field(default=None, description='The scope to request access to')


class OAuth2ClientAuthPreset(AuthPreset):
    request: OAuth2ClientRequestPreset


###########################
##### OAuth2 Password #####
###########################


class OAuth2PasswordUserPreset(UserPreset):
    clientId: str
    clientSecret: str
    username: str
    password: str


class OAuth2PasswordRequestPreset(RequestPreset):
    url: str = Field(description='The URL to request the authorization code')
    tokenUrl: str = Field(description='The URL to exchange the authorization code for an access token')
    clientMethod: AuthOAuthClientMethod = Field(
        default=AuthOAuthClientMethod.BASIC,
        description='The client authentication method for token endpoint.',
    )
    scope: str | None = Field(default=None, description='The scope to request access to')


class OAuth2PasswordAuthPreset(AuthPreset):
    request: OAuth2PasswordRequestPreset


###########################
##### OAuth2 Implicit #####
###########################


class OAuth2ImplicitUserPreset(UserPreset):
    clientId: str


class OAuth2ImplicitRequestPreset(RequestPreset):
    url: str = Field(description='The URL to request the authorization code')
    redirectUrl: str = Field(description='The URL to redirect to after authorization')
    webDriverCommmands: list[SeleniumCommand] = Field(description='The commands to execute in the web driver')
    clientMethod: AuthOAuthClientMethod = Field(
        default=AuthOAuthClientMethod.BASIC,
        description='The client authentication method for token endpoint.',
    )
    scope: str | None = Field(default=None, description='The scope to request access to')
    state: str | None = Field(default=None, description='The state is used to prevent CSRF attacks')


class OAuth2ImplicitAuthPreset(AuthPreset):
    """This OAuth2 flow requires a Webdriver."""

    request: OAuth2ImplicitRequestPreset


###########################
###### OAuth2 Refresh #####
###########################


class OAuth2RefreshUserPreset(UserPreset):
    refreshToken: str


class OAuth2RefreshProvider(AuthPreset):
    pass
