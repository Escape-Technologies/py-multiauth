from pydantic import Field

from multiauth.lib.presets.base import BasePreset, HTTPRequestParameters, UserPreset
from multiauth.lib.presets.cognito_base import AWSHashAlgorithm, AWSRegion

###########################
######### AWS SRP #########
###########################


class AWSSRPUserPreset(UserPreset):
    username: str
    password: str


class AWSSRPRequestPreset(HTTPRequestParameters):
    region: AWSRegion = Field(description='The region of the AWS service.')
    algorithm: AWSHashAlgorithm = Field(description='The hash algorithm used generate the signature.')
    poolId: int = Field(description='The pool ID of the AWS account.')
    clientId: int = Field(description='The client ID of the AWS account.')
    clientSecret: str = Field(description='The client secret of the AWS account.')


class AWSSRPBasePreset(BasePreset):
    request: AWSSRPRequestPreset
