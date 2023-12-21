"""Aws provider."""


from pydantic import BaseModel

from multiauth.entities.providers.aws import AuthHashalgorithmHawkandAWS


class AuthConfigHawk(BaseModel):

    """Authentication Configuration Parameters of the Hawk Method."""

    algorithm: AuthHashalgorithmHawkandAWS
    user: str | None
    nonce: str | None
    ext: str | None
    app: str | None
    dig: str | None
    timestamp: str | None
