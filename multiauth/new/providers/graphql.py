"""Implementation of the Rest authentication schema."""


from multiauth.entities.http import HTTPHeaders
from multiauth.entities.main import AuthResponse, AuthTech
from multiauth.new.entities.graphql import GraphQLAuthRequester, GraphQLCredentials
from multiauth.new.entities.main import (
    AuthExtractor,
    AuthInjector,
    AuthProvider,
    AuthRequester,
    Credentials,
)
from multiauth.new.main import http_standard_flow


def graphql_requester_to_standard(requester: GraphQLAuthRequester) -> AuthRequester:
    body = {'query': requester.query}
    headers = HTTPHeaders(requester.headers | {'Content-Type': 'application/json'})

    return AuthRequester(
        url=requester.url,
        method=requester.method,
        body=body,
        headers=headers,
        cookies=requester.cookies,
    )


def graphql_credentials_to_standard(credentials: GraphQLCredentials) -> Credentials:
    """Parse a GraphQLCredentials to a standard Credentials."""

    return Credentials(
        name=credentials.name,
        headers=credentials.headers,
        cookies=credentials.cookies,
        body={'variables': credentials.variables},
    )


def graphql_authenticator(schema: dict, user: dict, proxy: str | None) -> AuthResponse:
    """Authenticate a user using GraphQL."""

    gql_requester = GraphQLAuthRequester(**schema['requester'])
    requester = graphql_requester_to_standard(gql_requester)
    extractor = AuthExtractor(**schema['extractor'])
    injector = AuthInjector(**schema['injector'])

    provider = AuthProvider(requester=requester, extractor=extractor, injector=injector, refresher=None)

    gql_credentials = GraphQLCredentials(**user)
    credentials = graphql_credentials_to_standard(gql_credentials)

    return http_standard_flow(provider, AuthTech.GRAPHQL, credentials, proxy)
