from multiauth.new.entities.main import Credentials


class AWSRefreshCredentials(Credentials):
    refreshToken: str


class AWSSignatureCredentials(Credentials):
    accessKey: str
    secretKey: str


class AWSPasswordCredentials(Credentials):
    username: str
    password: str


class AWSSRPCredentials(Credentials):
    username: str
    password: str
