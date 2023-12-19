"""Implementation of the Rest authentication schema."""


from multiauth.entities.errors import AuthenticationError
from multiauth.entities.providers.http import (
    AuthRequester,
    Credentials,
    GraphQLAuthRequester,
    GraphQLCredentials,
)
from multiauth.providers.http_parser import parse_credentials, parser_requester


def graphql_parse_requester(schema: dict) -> GraphQLAuthRequester:
    requester = parser_requester(schema)

    if 'query' not in schema:
        raise AuthenticationError('Mandatory `requester.query` key is missing for GraphQLAuthentication')

    if not isinstance(schema['query'], str):
        raise AuthenticationError('`requester.query` must be a string for GraphQLAuthentication')

    return GraphQLAuthRequester(
        url=requester.url,
        method=requester.method,
        body=requester.body,
        headers=requester.headers,
        cookies=requester.cookies,
        query=schema['query'],
    )


def graphql_requester_to_standard(requester: GraphQLAuthRequester) -> AuthRequester:
    body = {'query': requester.query}
    headers = requester.headers | {'Content-Type': 'application/json'}

    return AuthRequester(
        url=requester.url,
        method=requester.method,
        body=body,
        headers=headers,
        cookies=requester.cookies,
    )


def graphql_parse_credentials(schema: dict) -> GraphQLCredentials:
    """Parse a raw dictionary to GraphQLCredentials."""

    credentials = parse_credentials(schema)

    if 'variables' not in schema:
        raise AuthenticationError('Mandatory `variables` key is missing from GraphQL credentials')

    if not isinstance(schema['variables'], dict):
        raise AuthenticationError('`variables` must be a dictionary in GraphQL credentials')

    return GraphQLCredentials(
        name=credentials.name,
        headers=credentials.headers,
        cookies=credentials.cookies,
        body=credentials.body,
        variables=schema['variables'],
    )


def graphql_credentials_to_standard(credentials: GraphQLCredentials) -> Credentials:
    """Parse a GraphQLCredentials to a standard Credentials."""

    return Credentials(
        name=credentials.name,
        headers=credentials.headers,
        cookies=credentials.cookies,
        body={'variables': credentials.variables},
    )
