import pytest

from multiauth.lib.token import JWTToken, SAMLToken, TokenType, extract_token, parse_jwt_token, parse_saml_token


# Fixture for valid JWT token
@pytest.fixture()
def valid_jwt_token() -> str:
    return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ0ZXN0SXNzdWVyIiwic3ViIjoiMTIzNDU2Nzg5MCIsImF1ZCI6InRlc3RBdWRpZW5jZSIsImV4cCI6MTYxNTkyOTIwMCwibmJmIjoxNjE1ODQyODAwLCJpYXQiOjE2MTU4NDI4MDAsImp0aSI6InRlc3RKVEkiLCJjdXN0b21GaWVsZCI6InRlc3RWYWx1ZSJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'  # noqa: E501


# Fixture for invalid JWT token
@pytest.fixture()
def invalid_jwt_token() -> str:
    return 'invalid.token.string'


# Tests for extract_token function
def test_extract_token_bearer(valid_jwt_token: str) -> None:
    assert extract_token(f'Bearer {valid_jwt_token}') == valid_jwt_token


def test_extract_token_cookie(valid_jwt_token: str) -> None:
    assert extract_token(f'token={valid_jwt_token}; Path=/; HttpOnly') == valid_jwt_token


def test_extract_token_raw_token(valid_jwt_token: str) -> None:
    assert extract_token(valid_jwt_token) == valid_jwt_token


def test_extract_token_non_bearer() -> None:
    non_bearer_str = 'Basic someRandomString'
    assert extract_token(non_bearer_str) == non_bearer_str


# Tests for jwt_token_analyzer function
def test_jwt_token_analyzer_valid(valid_jwt_token: str) -> None:
    jwt_info = parse_jwt_token(valid_jwt_token)
    assert isinstance(jwt_info, JWTToken)
    assert jwt_info.iss == 'testIssuer'
    assert jwt_info.sub == '1234567890'
    # Add more assertions based on expected token payload


def test_jwt_token_analyzer_invalid(invalid_jwt_token: str) -> None:
    assert parse_jwt_token(invalid_jwt_token) is None


# Fixture for valid JWT token
@pytest.fixture()
def valid_sample_token() -> str:
    # Sample SAML token for testing (this should be a string representation of a SAML XML)
    return """
    <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
        <saml:Issuer>SampleIssuer</saml:Issuer>
        <saml:Subject>
            <saml:NameID>SampleSubject</saml:NameID>
        </saml:Subject>
        <saml:Conditions NotBefore="2021-01-01T00:00:00Z" NotOnOrAfter="2021-01-02T00:00:00Z"/>
        <saml:AttributeStatement>
            <saml:Attribute Name="SampleAttribute">
                <saml:AttributeValue>SampleValue</saml:AttributeValue>
            </saml:Attribute>
        </saml:AttributeStatement>
        <saml:AuthnStatement>
            <saml:AuthnContext>
                <saml:AuthnContextClassRef>SampleAuthnContext</saml:AuthnContextClassRef>
            </saml:AuthnContext>
        </saml:AuthnStatement>
    </saml:Assertion>
    """


def test_parse_saml_token(valid_sample_token: str) -> None:
    token = parse_saml_token(valid_sample_token)
    assert token is not None
    assert isinstance(token, SAMLToken)
    assert token.type == TokenType.SAML
    assert token.issuer == 'SampleIssuer'
    assert token.subject == 'SampleSubject'
    assert token.notBefore.isoformat() == '2021-01-01T00:00:00'  # type: ignore[union-attr]
    assert token.notOnOrAfter.isoformat() == '2021-01-02T00:00:00'  # type: ignore[union-attr]
    assert token.attributes['SampleAttribute'] == 'SampleValue'
    assert token.authnContext == 'SampleAuthnContext'
