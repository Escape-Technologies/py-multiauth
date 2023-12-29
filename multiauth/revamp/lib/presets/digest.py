from pydantic import Field

from multiauth.entities.providers.digest import DigestHashAlgorithm
from multiauth.revamp.lib.presets.main import AuthInjector, AuthProvider, AuthRequester, Credentials


class DigestCredentials(Credentials):
    username: str
    password: str


class DigestAuthRequester(AuthRequester):
    pass


class DigestAuthInjector(AuthInjector):
    prefix: str = Field(default='Digest')
    algorithm: DigestHashAlgorithm = Field(
        default=DigestHashAlgorithm.MD5,
        description='The hash algorithm used to product the Digest token.',
    )
    domain: str | None = Field(default=None, description='The domain of the authentication.')
    realm: str | None = Field(
        default=None,
        description='The `realm` should contain at least the name of the host performing the authentication \
            and might additionally indicate the collection of users who might have access.',
    )
    nounce: str | None = Field(
        default=None,
        description='The `nounce` is used to prevent replay attacks and is used to prevent request forgery attacks.',
    )
    qop: str | None = Field(default=None, description='The quality of protection.')
    nc: str | None = Field(
        default=None,
        description='The `nonce count` indicates the number of times the client has reused the nonce value. \
            The server uses this value to detect and prevent replay attacks. \
            This value must be specified if and only if the `qop` is specified too.',
    )
    cnonce: str | None = Field(
        default=None,
        description='The `client nonce` must be specified if and only if the `qop` is specified too.',
    )
    opaque: str | None = Field(
        default=None,
        description='The opaque string is used to prevent request forgery attacks. \
        It is usually `base64` or `hex` encoded.',
    )


class DigestAuthProvider(AuthProvider):
    requester: DigestAuthRequester
    injector: DigestAuthInjector
