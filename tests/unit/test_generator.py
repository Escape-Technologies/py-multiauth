# pylint: disable=redefined-outer-name, unused-import, line-too-long, invalid-name

"""Test generator."""

from typing import Dict

import pytest

from multiauth.generator import _manual_fill, curl_to_escaperc

from .providers.test_manual_auth import auth, users_one_header, users_two_headers  # noqa


@pytest.fixture()
def graphql_curl_with_input_object_and_no_var() -> str:
    """Test auth schema."""
    return r"""curl --location --request POST 'https://qhgslipjmw.com/graphql' \
--header 'Content-Type: application/json' \
--data-raw '{"query":"mutation {\r\n    login(userLoginInput: {email: \"LoZhylgLX8@Nuz0bhEKMY.com\", password: \"8ua36eYKlN\"}){\r\n        token\r\n    }\r\n}","variables":{}}'"""


@pytest.fixture()
def graphql_curl_with_input_object_and_var() -> str:
    """Test auth schema."""
    return r"""curl --location --request POST 'https://qhgslipjmw.com/graphql' \
--header 'Content-Type: application/json' \
--data-raw '{"query":"mutation ($Login: UserLoginInput!){\r\n    login(userLoginInput: $Login){\r\n        token\r\n    }\r\n}","variables":{"Login":{"email":"LoZhylgLX8@Nuz0bhEKMY.com","password":"8ua36eYKlN"}}}'"""


@pytest.fixture()
def graphql_curl_with_normal_graphql_query() -> str:
    """Test auth schema."""
    return r"""curl --location --request POST 'https://www.terrang.fr/graphql' \
--header 'Content-Type: application/json' \
--data-raw '{"query":"mutation {\r\n    authenticateUser(username: \"ohtmjdkyhx@oergasjvhp.com\", password: \"Wj7UxfFTyzgPVM\"){\r\n        success\r\n    }\r\n}","variables":{"Login":{"email":"LoZhylgLX8@Nuz0bhEKMY.com","password":"8ua36eYKlN"}}}'"""


@pytest.fixture()
def rest_curl() -> str:
    """Test auth schema."""
    return r"""curl --location --request POST 'https://auth.ghqmcblmjc.com/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "email":"ohtmjdkyhx@oergasjvhp.com",
    "password":"Wj7UxfFTyzgPVM@"
}'"""


@pytest.fixture()
def rest_curl_not_json() -> str:
    """Test auth schema."""
    return r"""curl --location --request POST 'https://auth.ghqmcblmjc.com/login' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'email=ohtmjdkyhx@oergasjvhp.com' \
--data-urlencode 'password=Wj7UxfFTyzgPVM@'"""


@pytest.fixture()
def curl_no_data() -> str:
    """Test auth schema."""
    return r"""curl --location --request POST 'https://auth.ghqmcblmjc.com/login' \
--header 'Content-Type: application/x-www-form-urlencoded'"""


@pytest.fixture()
def graphql_curl_with_input_object_and_no_var_response() -> Dict:
    """Curl Response."""
    return {
        'users': {
            'user1': {
                'auth': 'schema1',
                'userLoginInput': {'email': 'LoZhylgLX8@Nuz0bhEKMY.com', 'password': '8ua36eYKlN'},
            },
        },
        'auth': {
            'schema1': {
                'tech': 'graphql',
                'url': 'https://qhgslipjmw.com/graphql',
                'method': 'POST',
                'mutation_name': 'login',
                'mutation_field': 'token',
                'options': {'operation': 'mutation', 'headers': {'Content-Type': 'application/json'}},
            },
        },
    }


@pytest.fixture()
def graphql_curl_with_input_object_and_var_response() -> Dict:
    """Curl Response."""
    return {
        'users': {
            'user1': {'auth': 'schema1', 'Login': {'email': 'LoZhylgLX8@Nuz0bhEKMY.com', 'password': '8ua36eYKlN'}},
        },
        'auth': {
            'schema1': {
                'tech': 'graphql',
                'url': 'https://qhgslipjmw.com/graphql',
                'method': 'POST',
                'mutation_name': 'login',
                'mutation_field': 'token',
                'options': {'operation': 'mutation', 'headers': {'Content-Type': 'application/json'}},
            },
        },
    }


@pytest.fixture()
def graphql_curl_with_normal_graphql_query_response() -> Dict:
    """Curl Response."""
    return {
        'users': {'user1': {'auth': 'schema1', 'username': 'ohtmjdkyhx@oergasjvhp.com', 'password': 'Wj7UxfFTyzgPVM'}},
        'auth': {
            'schema1': {
                'tech': 'graphql',
                'url': 'https://www.terrang.fr/graphql',
                'method': 'POST',
                'mutation_name': 'authenticateUser',
                'options': {'operation': 'mutation', 'headers': {'Content-Type': 'application/json'}},
            },
        },
    }


@pytest.fixture()
def rest_curl_response() -> Dict:
    """Curl Response."""
    return {
        'users': {'user1': {'auth': 'schema1', 'email': 'ohtmjdkyhx@oergasjvhp.com', 'password': 'Wj7UxfFTyzgPVM@'}},
        'auth': {
            'schema1': {
                'tech': 'rest',
                'url': 'https://auth.ghqmcblmjc.com/login',
                'method': 'POST',
                'options': {'headers': {'Content-Type': 'application/json'}},
            },
        },
    }


@pytest.fixture()
def rest_curl_not_json_response() -> Dict:
    """Curl Response."""
    return {
        'users': {'user1': {'auth': 'schema1', 'email': 'ohtmjdkyhx@oergasjvhp.com', 'password': 'Wj7UxfFTyzgPVM@'}},
        'auth': {
            'schema1': {
                'tech': 'rest',
                'url': 'https://auth.ghqmcblmjc.com/login',
                'method': 'POST',
                'options': {'headers': {'Content-Type': 'application/x-www-form-urlencoded'}},
            },
        },
    }


def test_serialize_headers(
    auth: Dict,
    users_one_header: Dict,
    users_two_headers: Dict,
) -> None:
    """Test serialize_headers."""

    headers_str = 'Authorization: Bearer 12345'
    headers_list = ['Authorization: Bearer 12345', 'Content-Type: application/json']
    headers_dict = {'Authorization': 'Bearer 12345', 'Content-Type': 'application/json'}

    rcfile = _manual_fill(headers_str)

    assert rcfile['auth'] == auth
    assert rcfile['users'] == users_one_header

    rcfile = _manual_fill(headers_list)

    assert rcfile['auth'] == auth
    assert rcfile['users'] == users_two_headers

    rcfile = _manual_fill(headers_dict)

    assert rcfile['auth'] == auth
    assert rcfile['users'] == users_two_headers


def test_graphql_curl_with_input_object_and_no_var(
    graphql_curl_with_input_object_and_no_var: str,
    graphql_curl_with_input_object_and_no_var_response: Dict,
) -> None:
    """Function that tests if the curl to escaperc works."""

    assert (
        curl_to_escaperc(graphql_curl_with_input_object_and_no_var)
        == graphql_curl_with_input_object_and_no_var_response
    )


def test_graphql_curl_with_input_object_and_var(
    graphql_curl_with_input_object_and_var: str,
    graphql_curl_with_input_object_and_var_response: Dict,
) -> None:
    """Function that tests if the curl to escaperc works."""

    assert curl_to_escaperc(graphql_curl_with_input_object_and_var) == graphql_curl_with_input_object_and_var_response


def test_graphql_curl_with_normal_graphql_query(
    graphql_curl_with_normal_graphql_query: str,
    graphql_curl_with_normal_graphql_query_response: Dict,
) -> None:
    """Function that tests if the curl to escaperc works."""

    assert curl_to_escaperc(graphql_curl_with_normal_graphql_query) == graphql_curl_with_normal_graphql_query_response


def test_rest_curl(
    rest_curl: str,
    rest_curl_response: Dict,
) -> None:
    """Function that tests if the curl to escaperc works."""

    assert curl_to_escaperc(rest_curl) == rest_curl_response


def test_rest_curl_not_json(
    rest_curl_not_json: str,
    rest_curl_not_json_response: Dict,
) -> None:
    """Function that tests if the curl to escaperc works."""

    assert curl_to_escaperc(rest_curl_not_json) == rest_curl_not_json_response


def test_curl_no_data(curl_no_data: str) -> None:
    """Function that tests if the curl to escaperc works."""

    assert curl_to_escaperc(curl_no_data) is None
