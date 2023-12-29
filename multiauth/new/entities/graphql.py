from typing import NewType

from pydantic import Field

from multiauth.entities.http import HTTPLocation
from multiauth.new.entities.main import (
    AuthExtractor,
    AuthInjector,
    AuthProvider,
    AuthRequester,
    Credentials,
)

GraphQLQuery = NewType('GraphQLQuery', str)


class GraphQLAuthRequester(AuthRequester):
    query: GraphQLQuery = Field(description='The tamplated GraphQL query to authenticate the user.')


class GraphQLAuthExtractor(AuthExtractor):
    location: HTTPLocation = Field(default=HTTPLocation.BODY)


class GraphQLAuthInjector(AuthInjector):
    pass


class AuthProviderGraphQL(AuthProvider):
    requester: GraphQLAuthRequester
    injector: GraphQLAuthInjector
    extractor: GraphQLAuthExtractor


class GraphQLCredentials(Credentials):
    variables: dict[str, str] = Field(description='The variables of the GraphQL query containing the user credentials.')
