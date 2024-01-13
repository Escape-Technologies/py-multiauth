from typing import NewType

from pydantic import Field

from multiauth.lib.http_core.entities import HTTPLocation
from multiauth.lib.presets.base_old import (
    AuthPreset,
    ExtractPreset,
    InjectPreset,
    RequestPreset,
    UserPreset,
)

GraphQLQuery = NewType('GraphQLQuery', str)


class GraphQLRequestPreset(RequestPreset):
    query: GraphQLQuery = Field(description='The tamplated GraphQL query to authenticate the user.')


class GraphQLExtractPreset(ExtractPreset):
    location: HTTPLocation = Field(default=HTTPLocation.BODY)


class GraphQLInjectPreset(InjectPreset):
    pass


class AuthPresetGraphQL(AuthPreset):
    request: GraphQLRequestPreset
    inject: GraphQLInjectPreset
    extract: GraphQLExtractPreset


class GraphQLUserPreset(UserPreset):
    variables: dict[str, str] = Field(description='The variables of the GraphQL query containing the user credentials.')
