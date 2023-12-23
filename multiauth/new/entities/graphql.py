from typing import NewType

from multiauth.new.entities.main import AuthRequester, Credentials

GraphQLQuery = NewType('GraphQLQuery', str)


class GraphQLAuthRequester(AuthRequester):
    query: GraphQLQuery


class GraphQLCredentials(Credentials):
    variables: dict[str, str]
