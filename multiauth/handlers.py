"""Parse a response to extract auth credentials."""

from typing import Dict, Optional

from multiauth.entities.http import HTTPMethod
from multiauth.entities.main import AuthResponse, AuthTech
from multiauth.manager import User
from multiauth.providers import (
    apikey_authenticator,
    aws_authenticator,
    aws_reauthenticator,
    basic_authenticator,
    digest_authenticator,
    graphql_authenticator,
    manual_authenticator,
    oauth_authenticator,
    oauth_reauthenticator,
    rest_authenticator,
)
from multiauth.providers.graphql import graphql_reauthenticator
from multiauth.providers.rest import rest_reauthenticator
from multiauth.providers.webdriver.routine import webdriver_authenticator


# pylint: disable=no-else-return, too-many-return-statements
def auth_handler(
    schemas: Dict,
    user: User,
    method: Optional[HTTPMethod] = None,
) -> Optional[AuthResponse]:
    """Handles the authentication and returns the authentication response.

    This function takes the current working user as input and checks the schema that the user needs. After getting the schema, it executes the appropriate
    authenticator according the tech found in the schema.
    """

    # Fetch authentication schema from users
    schema = schemas[user.auth_schema]

    authentication: AuthTech = user.auth_tech
    response: Optional[AuthResponse] = None
    if authentication == AuthTech.APIKEY:
        response = apikey_authenticator(user, schema)

    elif authentication == AuthTech.AWS:
        response = aws_authenticator(user, schema)

    elif authentication == AuthTech.BASIC:
        response = basic_authenticator(user, schema)

    elif authentication == AuthTech.REST:
        response = rest_authenticator(user, schema)

    elif authentication == AuthTech.WEBDRIVER:
        response = webdriver_authenticator(user, schema)

    # The method parameter added is due to the fact the digest uses the method when hashing
    # Although GraphQL apps use POST by default, we use GET in some of our test
    elif authentication == AuthTech.DIGEST:
        response = digest_authenticator(user, schema, method)

    elif authentication == AuthTech.GRAPHQL:
        response = graphql_authenticator(user, schema)

    elif authentication == AuthTech.HAWK:
        pass

    elif authentication == AuthTech.OAUTH:
        response = oauth_authenticator(user, schema)

    elif authentication == AuthTech.MANUAL:
        response = manual_authenticator(user)

    elif authentication == AuthTech.PUBLIC:
        response = None

    return response


def reauth_handler(
    schemas: Dict,
    user: User,
    refresh_token: str,
) -> Optional[AuthResponse]:
    """Handles the reauthentication and returns the new authentication response.

    This function takes the current working user as input and checks the schema that the user needs. After getting the schema, it executes the appropriate
    reauthentication according the tech found in the schema.
    """

    schema = schemas[user.auth_schema]
    authentication = user.auth_tech

    # For now we only have reauthentication with OAuth
    if authentication == AuthTech.OAUTH:
        return oauth_reauthenticator(user, schema, refresh_token)

    elif authentication == AuthTech.AWS:
        return aws_reauthenticator(user, schema, refresh_token)

    elif authentication == AuthTech.REST:
        return rest_reauthenticator(user, schema, refresh_token)

    elif authentication == AuthTech.GRAPHQL:
        return graphql_reauthenticator(user, schema, refresh_token)

    elif authentication == AuthTech.WEBDRIVER:
        return webdriver_authenticator(user, schema)

    return None
