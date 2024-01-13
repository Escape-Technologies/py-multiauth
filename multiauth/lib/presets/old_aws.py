import enum

from pydantic import Field

from multiauth.lib.presets.base_old import AuthPreset, RequestPreset, UserPreset

###########################
## TODO(maxence@escape, antoine@escape): We should stop doing that and use this method: https://stackoverflow.com/questions/58833462/aws-cognito-authentication-curl-call-generate-token-without-cli-no-clien
###########################


class AWSRegion(enum.StrEnum):
    US_EAST_OHIO = 'us-east-2'
    US_EAST_N_VIRGINIA = 'us-east-1'
    US_WEST_N_CALIFORNIA = 'us-west-1'
    US_WEST_OREGON = 'us-west-2'
    AFRICA_CAPE_TOWN = 'af-south-1'
    ASIA_PACIFIC_HONG_KONG = 'ap-east-1'
    ASIA_PACIFIC_MUMBAI = 'ap-south-1'
    ASIA_PACIFIC_OSAKA = 'ap-northeast-3'
    ASIA_PACIFIC_SEOUL = 'ap-northeast-2'
    ASIA_PACIFIC_SINGAPORE = 'ap-southeast-1'
    ASIA_PACIFIC_SYDNEY = 'ap-southeast-2'
    ASIA_PACIFIC_TOKYO = 'ap-northeast-1'
    CANADA_CENTRAL = 'ca-central-1'
    CHINA_BEIJING = 'cn-north-1'
    CHINA_NINGXIA = 'cn-northwest-1'
    EUROPE_FRANKFURT = 'eu-central-1'
    EUROPE_IRELAND = 'eu-west-1'
    EUROPE_LONDON = 'eu-west-2'
    EUROPE_MILAN = 'eu-south-1'
    EUROPE_PARIS = 'eu-west-3'
    EUROPE_STOCKHOLM = 'eu-north-1'
    MIDDLE_EAST_BAHRAIN = 'me-south-1'
    SOUTH_AMERICA_SAO_PAULO = 'sa-east-1'


class AWSHashAlgorithm(enum.StrEnum):
    SHA_256 = 'SHA256'
    SHA_1 = 'SHA1'


###########################
######### AWS SRP #########
###########################


class AWSSRPUserPreset(UserPreset):
    username: str
    password: str


class AWSSRPRequestPreset(RequestPreset):
    region: AWSRegion = Field(description='The region of the AWS service.')
    algorithm: AWSHashAlgorithm = Field(description='The hash algorithm used generate the signature.')
    poolId: int = Field(description='The pool ID of the AWS account.')
    clientId: int = Field(description='The client ID of the AWS account.')
    clientSecret: str = Field(description='The client secret of the AWS account.')


class AWSSRPAuthPreset(AuthPreset):
    request: AWSSRPRequestPreset


###########################
###### AWS Signature ######
###########################
class AWSSignatureUserPreset(UserPreset):
    accessKey: str
    secretKey: str


class AWSSignatureRequestPreset(RequestPreset):
    region: AWSRegion = Field(description='The region of the AWS service.')
    algorithm: AWSHashAlgorithm = Field(description='The hash algorithm used generate the signature.')
    service: str = Field(description='The service of the AWS account.')


class AWSSignatureAuthPreset(AuthPreset):
    request: AWSSignatureRequestPreset


###########################
###### AWS Password ######
###########################


class AWSPasswordUserPreset(UserPreset):
    username: str
    password: str


class AWSPasswordRequestPreset(RequestPreset):
    region: AWSRegion = Field(description='The region of the AWS service.')
    clientId: int = Field(description='The client ID of the AWS account.')
    clientSecret: str = Field(description='The client secret of the AWS account.')


class AWSPasswordAuthPreset(AuthPreset):
    request: AWSPasswordRequestPreset


###########################
####### AWS Refresh #######
###########################


class AWSRefreshUserPreset(UserPreset):
    refreshToken: str


class AWSRefreshRequestPreset(RequestPreset):
    region: AWSRegion = Field(description='The region of the AWS service.')
    clientId: int = Field(description='The client ID of the AWS account.')
    clientSecret: str = Field(description='The client secret of the AWS account.')


class AWSRefreshAuthPreset(AuthPreset):
    request: AWSRefreshRequestPreset
