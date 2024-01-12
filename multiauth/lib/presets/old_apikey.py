from pydantic import Field

from multiauth.lib.presets.old_main import AuthInjector, AuthProvider, Credentials


class APIKeyCredentials(Credentials):
    apiKey: str = Field(description='The API key of the user.')


class APIKeyAuthInjector(AuthInjector):
    key: str = Field(
        default='x-api-key',
        description='The name of parameter (header or cookie) containing the API key.',
    )


class APIKeyAuthProvider(AuthProvider):
    injector: APIKeyAuthInjector
