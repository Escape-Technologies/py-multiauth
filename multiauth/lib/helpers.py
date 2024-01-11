import base64
import json
from http.cookies import SimpleCookie

from pydantic import BaseModel


class JWTToken(BaseModel):

    """This class finds all the registered claims in the JWT token payload.

    Attributes:
        sig: Signature algorthm used in the JWT token.
        iss: Issuer of the JWT token.
        sub: Subject of the JWT token.
        aud: Audience of the JWT token -> intended for.
        exp: Expiration time of the JWT token.
        nbf: Identifies the time before which the JWT token is not yet valid.
        iat: Issued at time of the JWT token.
        jti: JWT token identifier.
        other: Other claims in the JWT token.
    """

    sig: str
    iss: str | None
    sub: str | None
    aud: str | None
    exp: int | None
    nbf: int | None
    iat: int | None
    jti: str | None
    other: dict


def extract_token(string: str) -> str:
    """Extracts a token from a string that could be an authorization header or a cookie."""
    # Handling Bearer tokens

    if string.lower().startswith('bearer '):
        return string[7:]

    # Handling Cookie headers using SimpleCookie
    try:
        cookie: SimpleCookie = SimpleCookie()
        cookie.load(string)
        for key, morsel in cookie.items():
            if 'token' in key.lower():
                return morsel.value
    except Exception:
        return string

    # Assuming the string is a token if no other format is recognized
    return string


def jwt_token_analyzer(token: str) -> JWTToken:
    """This function transforms a JWT token into a defined datatype."""

    token = extract_token(token)

    # Step 2: Base64 Decode (JWT specific)
    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError('Invalid JWT token format')

    token_header: str = parts[0]
    token_payload: str = parts[1]

    header = json.loads(base64.urlsafe_b64decode(token_header + '=' * (-len(token_header) % 4)))
    payload = json.loads(base64.urlsafe_b64decode(token_payload + '=' * (-len(token_payload) % 4)))

    return JWTToken(
        sig=header['alg'],
        iss=payload.pop('iss', None),
        sub=payload.pop('sub', None),
        aud=payload.pop('aud', None),
        exp=payload.pop('exp', None),
        nbf=payload.pop('nbf', None),
        iat=payload.pop('iat', None),
        jti=payload.pop('jti', None),
        other=header | payload,
    )
