from pydantic import Field

from multiauth.lib.presets.base import BasePreset, HTTPRequestParameters, UserPreset
from multiauth.lib.presets.cognito_base import AWSRegion

###########################
####### AWS Refresh #######
###########################


class AWSRefreshUserPreset(UserPreset):
    refreshToken: str


class AWSRefreshRequestPreset(HTTPRequestParameters):
    region: AWSRegion = Field(description='The region of the AWS service.')
    clientId: int = Field(description='The client ID of the AWS account.')
    clientSecret: str = Field(description='The client secret of the AWS account.')


class AWSRefreshBasePreset(BasePreset):
    request: AWSRefreshRequestPreset
