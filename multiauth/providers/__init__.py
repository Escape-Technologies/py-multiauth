"""Auth Providers."""

from multiauth.providers.apikey import apikey_authenticator
from multiauth.providers.aws import aws_authenticator, aws_reauthenticator
from multiauth.providers.basic import basic_authenticator
from multiauth.providers.digest import digest_authenticator
from multiauth.providers.graphql import graphql_authenticator
from multiauth.providers.manual import manual_authenticator
from multiauth.providers.oauth import oauth_authenticator, oauth_reauthenticator
from multiauth.providers.rest import rest_authenticator
from multiauth.providers.webdriver import webdriver_authenticator
