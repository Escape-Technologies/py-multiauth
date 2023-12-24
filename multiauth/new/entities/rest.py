from typing import Any

from pydantic import Field

from multiauth.new.entities.main import (
    AuthExtractor,
    AuthInjector,
    AuthProvider,
    AuthRefresher,
    AuthRequester,
    Credentials,
)


class RESTCredentials(Credentials):
    body: Any | None


class RESTAuthRequester(AuthRequester):
    pass


class RESTAuthInjector(AuthInjector):
    pass


class RESTAuthExtractor(AuthExtractor):
    pass


class RESTAuthProvider(AuthProvider):
    requester: RESTAuthRequester
    injector: RESTAuthInjector
    extractor: RESTAuthExtractor
    refresher: AuthRefresher | None = Field(default=None)
