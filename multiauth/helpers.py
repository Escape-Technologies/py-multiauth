#pylint: disable=no-name-in-module

"""Helper functions for the authentication process."""

import base64
import hashlib
import hmac
import json
import re
import sys
from json.decoder import JSONDecodeError
from typing import Any, Match, cast

import jwt
import requests

from multiauth.types.errors import AuthenticationError
from multiauth.types.main import AuthHashAlgorithmDigest, AuthResponse, AuthTech, JWTToken, Token
from multiauth.types.providers.oauth import AuthOAuthlocation
from multiauth.utils import dict_nested_get

try:
    from PyQt5.QtCore import QUrl, pyqtSignal  # type: ignore[import]
    from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor  # type: ignore[import]
    from PyQt5.QtWebEngineWidgets import QWebEngineView  # type: ignore[import]
    from PyQt5.QtWidgets import QApplication, QDesktopWidget  # type: ignore[import]
    PYQT5_ERROR = None
except ImportError as error:
    PYQT5_ERROR = error


def extract_token(
    response: requests.Response,
    tech: AuthTech,
    headers: dict[str, str],
    refresh_token_name: str | None = None,
) -> tuple[AuthResponse, str | None]:
    """This function takes the response and tries to extract the tokens.

    This function is mainly a helper function to the REST and the GraphQL authenctication schema. The goal of the function is to generate the authentication
    response according to the extracted tokens from the repsonse
    """

    def _find_token(token: Any, response: Any) -> Any:
        """This function finds the value of the token."""
        result = response

        if len(token) > 0:
            token_name = token[0]
            res_token_name: Any = dict_nested_get(result, token_name)
            result = _find_token(token[1:], res_token_name)

        return result

    if response.status_code is None or response.status_code >= 400:
        raise AuthenticationError(f'Response returned for authentication has failed: {response.text}')

    try:
        response_dict = json.loads(response.text)
    except JSONDecodeError as e:
        raise AuthenticationError(f'{type(e).__name__}: Response returned by authentication server is invalid: {e}') from e

    headers_to_add: dict = {}

    if headers is not None:
        for header_name, header_arg in headers.items():
            while '{{' in header_arg and '}}' in header_arg:

                #regex to find the name of the token inside {{token_name}}
                token_name = cast(Match, re.search('{{(.*)}}', header_arg)).group(1)

                #retrived token from the response
                res_token = _find_token(token_name.split('.'), response_dict)

                try:
                    assert res_token is not None
                except AssertionError as e:
                    raise AuthenticationError(f'{type(e).__name__}: The Authentication token wasn\'t fetched properly.') from e
                header_arg = header_arg.replace('{{' + token_name + '}}', res_token)
            headers_to_add[header_name] = header_arg

    # Here we are going to retrieve the refresh token from the response
    if refresh_token_name is not None:
        refresh_token: str = _find_token(refresh_token_name.split('.'), response_dict)
        return AuthResponse(tech=tech, headers=headers_to_add), refresh_token

    return AuthResponse(tech=tech, headers=headers_to_add), None


def hash_calculator(hash_type: AuthHashAlgorithmDigest, input_data: str | bytes) -> str:
    """This function determines the appropriate hashing function and returns the hashing of the input."""

    if hash_type in (AuthHashAlgorithmDigest.MD5, AuthHashAlgorithmDigest.MD5_SESS):
        if isinstance(input_data, str):
            input_data = input_data.encode('utf-8')
        return hashlib.md5(input_data).hexdigest()

    if hash_type in (AuthHashAlgorithmDigest.SHA_256, AuthHashAlgorithmDigest.SHA_256_SESS):
        if isinstance(input_data, str):
            input_data = input_data.encode('utf-8')
        return hashlib.sha256(input_data).hexdigest()

    if hash_type in (AuthHashAlgorithmDigest.SHA_512_256, AuthHashAlgorithmDigest.SHA_512_256_SESS):
        if isinstance(input_data, str):
            input_data = input_data.encode('utf-8')
        return hashlib.sha512(input_data).hexdigest()

    return ''


def token_endpoint_auth_method(auth_location: AuthOAuthlocation) -> str:
    """This function takes the authorization location that is provided in the configuration and determines which token endpoint authentication method should be
    used by the session."""

    if auth_location == AuthOAuthlocation.BODY:
        return 'client_secret_post'
    if auth_location == AuthOAuthlocation.BASIC:
        return 'client_secret_basic'

    return ''


def get_secret_hash(username: str, client_id: str, client_secret: str) -> str:
    """This function calculates the secret hash used in the AWS cognito authentication in case the client secret is provided."""

    message = bytearray(username + client_id, 'utf-8')
    hmac_obj = hmac.new(bytearray(client_secret, 'utf-8'), message, hashlib.sha256)
    return base64.standard_b64encode(hmac_obj.digest()).decode('utf-8')


#pylint: disable=too-few-public-methods
def authentication_portal(url: str, callback_url: str) -> tuple[int, str]:
    """This function will open up a browser for the user to enter his credentials during OAuth."""

    if not PYQT5_ERROR:
        raise ImportError('PyQT5 unavailable. Please install it properly.') from PYQT5_ERROR

    class RequestInterceptor(QWebEngineUrlRequestInterceptor):

        """This class is used to intercept all the requests sent my the browser."""
        # Creating the Signal to be sent
        found: pyqtSignal = pyqtSignal(int)

        # A variable to store the link that was found
        result: str = ''

        def __init__(self, callback_url: str) -> None:
            """Constructor."""
            super().__init__()
            self.callback_url = callback_url

        # pylint: disable=invalid-name
        def interceptRequest(self, info: Any) -> None:
            """Request Interceptor."""
            if self.callback_url in info.requestUrl().toString():
                self.result = info.requestUrl().toString()

                # Emit the signal for the main applicaiton to process
                self.found.emit(1)

    # Creating an application instance and providing it with system parameters
    app = QApplication(sys.argv)

    # Creating a Web Engine Window
    browser = QWebEngineView()

    # Giving the window a URL to open and a Title
    browser.load(QUrl(url))
    browser.setWindowTitle('Authentication Portal')

    # Resize screen
    browser.resize(1200, 1000)

    # Taking the Rectangle forming the window
    geometry = browser.frameGeometry()

    # QDesktopWidget provides information about the screen of the computer
    # availableGeometry returns the rectangle which forms the screen of the computer
    # center returns the center point of the screen
    center_point = QDesktopWidget().availableGeometry().center()

    # Make the Center point of the rectangle the center point of the screen
    geometry.moveCenter(center_point)

    # move the browser
    # since move uses the topleft point as a reference, give the top left point of ht browser
    browser.move(geometry.topLeft())

    # Now we want to create attach the interceptor to the web application
    request_interceptor = RequestInterceptor(callback_url)
    browser.page().profile().setUrlRequestInterceptor(request_interceptor)

    # If the string is found, exit the browser
    request_interceptor.found.connect(app.exit)

    browser.show()

    # It is important to note the exit codes
    # exit_code '0' means that the application was closed before getting the url
    # exit_code '1' means that the application was closed forcefully, and we got the URL
    # So exit_code '1' good :) and exit_code '0' bad :(
    return app.exec_(), request_interceptor.result


def jwt_token_analyzer(token: Token) -> JWTToken:
    """This function transforms a JWT token into a defined datatype."""

    # First verify the JWT signature
    try:
        _ = jwt.decode(token, options={'verify_signature': False, 'verify_exp': False})
    except Exception as e:
        raise AuthenticationError('The token provided is not a JWT token') from e

    # First of all we need to decrypt the token
    seperated_token = token.split('.')
    token_header: str = seperated_token[0]
    token_payload: str = seperated_token[1]

    header: dict = json.loads(base64.urlsafe_b64decode(token_header + '=' * (-len(token_header) % 4)))
    payload: dict = json.loads(base64.urlsafe_b64decode(token_payload + '=' * (-len(token_payload) % 4)))

    return JWTToken({
        'sig': header['alg'],
        'iss': payload.pop('iss', None),
        'sub': payload.pop('sub', None),
        'aud': payload.pop('aud', None),
        'exp': payload.pop('exp', None),
        'nbf': payload.pop('nbf', None),
        'iat': payload.pop('iat', None),
        'jti': payload.pop('jti', None),
        'other': payload
    })


# def jwt_token_module(token: Token) -> None:
#     """This function takes in a JWT token as an input and analyzes the token and finally returns some alerts regarding the JWT token."""

#     # First verify the JWT signature
#     try:
#         _ = jwt.decode(token, options={'verify_signature': False, 'verify_exp': False})
#     except Exception:
#         raise AuthenticationError('The token provided is not a JWT token')

#     # First divide the token into the header, payload, and signature
#     seperated_token = token.split('.')
#     token_header: str = seperated_token[0]
#     token_payload: str = seperated_token[1]
#     token_signature: str = seperated_token[2]

#     def _decode(string: Token) -> dict:
#         return json.loads(base64.urlsafe_b64decode(string + '=' * (-len(string) % 4)))

#     def _encode(string: dict) -> Token:
#         return base64.urlsafe_b64encode(json.dumps(string, separators=(',', ':')).encode()).decode('UTF-8').strip('=')

#     def _check_none_alg(token_header: str, token_payload: str) -> list[Token]:
#         """This function creates tokens with None signature."""

#         algorithms: list[str] = ['none', 'None', 'NONE', 'nOnE']
#         token_header_decoded: dict = _decode(token_header)
#         result: list[str] = []

#         for algorithm in algorithms:
#             try:
#                 token_header_decoded['alg'] = algorithm
#             except KeyError:
#                 raise AuthenticationError('The header of the JWT token does not contain alg section')

#             result.append(_encode(token_header_decoded) + '.' + token_payload + '.')

#         return result

#     def _check_null_signature(token_header: str, token_payload: str) -> Token:
#         """This function creates a token with just null signature.

#         No changing of signing algorithm
#         """

#         return token_header + '.' + token_payload + '.'

#     def _check_hs_signature(token_header: str, token_payload: str) -> list[Token]:
#         """This function checks if it is possible to use a token with simply an hash signature."""

#         result: list[str] = []

#         # For sha512
#         new_header = _decode(deepcopy(token_header))
#         new_header['alg'] = 'HS512'
#         _new_header = _encode(new_header)
#         content = _new_header + '.' + token_payload
#         signature_hash_512 = base64.urlsafe_b64encode(hmac.new(''.encode(), content.encode(), hashlib.sha512).digest()).decode('UTF-8').strip()
#         result.append(content + '.' + signature_hash_512)

#         # For sha256
#         new_header = _decode(deepcopy(token_header))
#         new_header['alg'] = 'HS256'
#         _new_header = _encode(new_header)
#         content = _new_header + '.' + token_payload
#         signature_hash_256 = base64.urlsafe_b64encode(hmac.new(''.encode(), content.encode(), hashlib.sha256).digest()).decode('UTF-8').strip()
#         result.append(content + '.' + signature_hash_256)

#         # For sha384
#         new_header = _decode(deepcopy(token_header))
#         new_header['alg'] = 'HS384'
#         _new_header = _encode(new_header)
#         content = _new_header + '.' + token_payload
#         signature_hash_384 = base64.urlsafe_b64encode(hmac.new(''.encode(), content.encode(), hashlib.sha384).digest()).decode('UTF-8').strip()
#         result.append(content + '.' + signature_hash_384)

#         return result

#     def _check_rsa_embed(token_header: str, token_payload: str) -> Token:
#         """Check in case the signature that RSA based."""

#         def _get_rsa_key_pair() -> tuple[Any, Any]:
#             """Generate RSA keys."""

#             # generate private/public key pair
#             key = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=2048)

#             # get public key in OpenSSH format
#             public_key = key.public_key().public_bytes(serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH)

#             # get private key in PEM container format
#             pem = key.private_bytes(
#                 encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption()
#             )

#             # decode to printable strings
#             private_key_str = pem.decode('utf-8')
#             public_key_str = public_key.decode('utf-8')

#             return private_key_str, public_key_str

#         priv_key, pub_key = _get_rsa_key_pair()
