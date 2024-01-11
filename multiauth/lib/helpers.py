import base64
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from enum import StrEnum
from http.cookies import SimpleCookie

from pydantic import BaseModel


class TokenType(StrEnum):
    JWT = 'JWT'
    SAML = 'SAML'


class Token(BaseModel):
    """This class represents a generic token."""

    raw: str
    type: TokenType


class JWTToken(Token):

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


class SAMLToken(Token):
    issuer: str | None = None
    subject: str | None = None
    notBefore: datetime | None = None
    notOnOrAfter: datetime | None = None
    attributes: dict[str, str] = {}
    authnContext: str | None = None


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


def parse_saml_token(token: str) -> SAMLToken | None:
    """Extracts a SAML token into a SAMLToken object."""

    token = extract_token(token)

    try:
        root = ET.fromstring(token)
        namespace = {'saml': 'urn:oasis:names:tc:SAML:2.0:assertion'}

        issuer = root.find('.//saml:Issuer', namespace)
        subject = root.find('.//saml:Subject/saml:NameID', namespace)
        conditions = root.find('.//saml:Conditions', namespace)
        attributes: dict[str, str] = {}

        for attr in root.findall('.//saml:AttributeStatement/saml:Attribute', namespace):
            if ((attr_name := attr.get('Name')) is not None) and (
                (attr_val := attr.find('.//saml:AttributeValue', namespace)) is not None
            ):
                attributes[attr_name] = attr_val.text or ''

        authn_context = root.find('.//saml:AuthnContextClassRef', namespace)

        return SAMLToken(
            raw=token,
            type=TokenType.SAML,
            issuer=issuer.text if issuer is not None else None,
            subject=subject.text if subject is not None else None,
            notBefore=datetime.strptime(conditions.get('NotBefore', ''), '%Y-%m-%dT%H:%M:%SZ')
            if conditions is not None and conditions.get('NotBefore')
            else None,
            notOnOrAfter=datetime.strptime(conditions.get('NotOnOrAfter', ''), '%Y-%m-%dT%H:%M:%SZ')
            if conditions is not None and conditions.get('NotOnOrAfter')
            else None,
            attributes=attributes,
            authnContext=authn_context.text if authn_context is not None else None,
        )
    except Exception:
        return None


def parse_jwt_token(token: str) -> JWTToken | None:
    """This function transforms a JWT token into a defined datatype."""

    token = extract_token(token)

    try:
        # Step 2: Base64 Decode (JWT specific)
        parts = token.split('.')
        if len(parts) != 3:
            return None

        token_header: str = parts[0]
        token_payload: str = parts[1]

        header = json.loads(base64.urlsafe_b64decode(token_header + '=' * (-len(token_header) % 4)))
        payload = json.loads(base64.urlsafe_b64decode(token_payload + '=' * (-len(token_payload) % 4)))

        return JWTToken(
            raw=token,
            type=TokenType.JWT,
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
    except Exception:
        return None


def parse_token(token: str) -> Token | None:
    """This function transforms a token into a defined datatype."""

    res: Token | None

    res = parse_jwt_token(token)
    if res is not None:
        return res
    res = parse_saml_token(token)
    if res is not None:
        return res

    return None


def extract_expiration_date(token: JWTToken | SAMLToken) -> int | None:
    """Extracts the expiration date from a JWT token."""

    if isinstance(token, JWTToken):
        return token.exp
    if isinstance(token, SAMLToken):
        return int(token.notOnOrAfter.timestamp()) if token.notOnOrAfter is not None else None

    return None
