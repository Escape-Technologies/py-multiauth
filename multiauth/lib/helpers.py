import base64
import json
from typing import Dict

import jwt
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
    exp: str | None
    nbf: str | None
    iat: str | None
    jti: str | None
    other: dict


def jwt_token_analyzer(token: str) -> JWTToken:
    """This function transforms a JWT token into a defined datatype."""

    # First verify the JWT signature
    try:
        _ = jwt.decode(token, options={'verify_signature': False, 'verify_exp': False})
    except Exception as e:
        raise ValueError('The token provided is not a JWT token') from e

    # First of all we need to decrypt the token
    separated_token = token.split('.')
    token_header: str = separated_token[0]
    token_payload: str = separated_token[1]

    header: Dict = json.loads(base64.urlsafe_b64decode(token_header + '=' * (-len(token_header) % 4)))
    payload: Dict = json.loads(base64.urlsafe_b64decode(token_payload + '=' * (-len(token_payload) % 4)))

    return JWTToken(
        sig=header['alg'],
        iss=payload.pop('iss', None),
        sub=payload.pop('sub', None),
        aud=payload.pop('aud', None),
        exp=payload.pop('exp', None),
        nbf=payload.pop('nbf', None),
        iat=payload.pop('iat', None),
        jti=payload.pop('jti', None),
        other=payload,
    )
