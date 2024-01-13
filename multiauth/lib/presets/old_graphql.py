from typing import NewType

from pydantic import Field

from multiauth.lib.http_core.entities import HTTPLocation
from multiauth.lib.presets.base import (
    BaseExtraction,
    BaseInjection,
    BasePreset,
    HTTPRequestParameters,
    UserPreset,
)

GraphQLQuery = NewType('GraphQLQuery', str)


class GraphQLRequestPreset(HTTPRequestParameters):
    query: GraphQLQuery = Field(description='The tamplated GraphQL query to authenticate the user.')


class GraphQLExtractPreset(BaseExtraction):
    location: HTTPLocation = Field(default=HTTPLocation.BODY)


class GraphQLInjectPreset(BaseInjection):
    pass


class BasePresetGraphQL(BasePreset):
    request: GraphQLRequestPreset
    inject: GraphQLInjectPreset
    extract: GraphQLExtractPreset


class GraphQLUserPreset(UserPreset):
    variables: dict[str, str] = Field(description='The variables of the GraphQL query containing the user credentials.')
