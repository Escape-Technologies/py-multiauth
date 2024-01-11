import pytest

from multiauth.lib.helpers import JWTToken, extract_token, jwt_token_analyzer


# Fixture for valid JWT token
@pytest.fixture()
def valid_jwt_token() -> str:
    return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ0ZXN0SXNzdWVyIiwic3ViIjoiMTIzNDU2Nzg5MCIsImF1ZCI6InRlc3RBdWRpZW5jZSIsImV4cCI6MTYxNTkyOTIwMCwibmJmIjoxNjE1ODQyODAwLCJpYXQiOjE2MTU4NDI4MDAsImp0aSI6InRlc3RKVEkiLCJjdXN0b21GaWVsZCI6InRlc3RWYWx1ZSJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'


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
    jwt_info = jwt_token_analyzer(valid_jwt_token)
    assert isinstance(jwt_info, JWTToken)
    assert jwt_info.iss == 'testIssuer'
    assert jwt_info.sub == '1234567890'
    # Add more assertions based on expected token payload


def test_jwt_token_analyzer_invalid(invalid_jwt_token: str) -> None:
    with pytest.raises(ValueError):
        jwt_token_analyzer(invalid_jwt_token)


# Additional tests can be added for edge cases and error handling
