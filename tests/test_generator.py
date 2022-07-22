#pylint: disable=redefined-outer-name, unused-import, line-too-long, invalid-name

"""Test generator."""
import pytest

from multiauth.generator import curl_to_escaperc, raw_headers_to_manual

from .providers.test_manual_auth import auth, users_one_header, users_two_headers  # noqa


@pytest.fixture
def graphql_curl_with_input_object_and_no_var() -> str:
    """Test auth schema."""
    return r"""curl --location --request POST 'https://apismxu6skxg-backend.functions.fnc.fr-par.scw.cloud/graphql' \
--header 'Content-Type: application/json' \
--data-raw '{"query":"mutation {\r\n    login(userLoginInput: {email: \"karim.rustom@escape.tech\", password: \"frenchfries\"}){\r\n        token\r\n    }\r\n}","variables":{}}'"""


@pytest.fixture
def graphql_curl_with_input_object_and_var() -> str:
    """Test auth schema."""
    return r"""curl --location --request POST 'https://apismxu6skxg-backend.functions.fnc.fr-par.scw.cloud/graphql' \
--header 'Content-Type: application/json' \
--data-raw '{"query":"mutation ($Login: UserLoginInput!){\r\n    login(userLoginInput: $Login){\r\n        token\r\n    }\r\n}","variables":{"Login":{"email":"karim.rustom@escape.tech","password":"frenchfries"}}}'"""


@pytest.fixture
def graphql_curl_with_normal_graphql_query() -> str:
    """Test auth schema."""
    return r"""curl --location --request POST 'https://www.terrang.fr/graphql' \
--header 'Content-Type: application/json' \
--data-raw '{"query":"mutation {\r\n    authenticateUser(username: \"jw.anon.5172@gmail.com\", password: \"Wj7UxfFTyzgPVM\"){\r\n        success\r\n    }\r\n}","variables":{"Login":{"email":"karim.rustom@escape.tech","password":"frenchfries"}}}'"""


@pytest.fixture
def rest_curl() -> str:
    """Test auth schema."""
    return r"""curl --location --request POST 'https://auth.console.fauna.com/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "email":"jw.anon.5172@gmail.com",
    "password":"Wj7UxfFTyzgPVM@"
}'"""


@pytest.fixture
def rest_curl_not_json() -> str:
    """Test auth schema."""
    return r"""curl --location --request POST 'https://auth.console.fauna.com/login' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'email=jw.anon.5172@gmail.com' \
--data-urlencode 'password=Wj7UxfFTyzgPVM@'"""


@pytest.fixture
def curl_no_data() -> str:
    """Test auth schema."""
    return r"""curl --location --request POST 'https://auth.console.fauna.com/login' \
--header 'Content-Type: application/x-www-form-urlencoded'"""


@pytest.fixture
def graphql_curl_with_input_object_and_no_var_response() -> dict:
    """Curl Response."""
    return {
        'users': {
            'user1': {
                'auth': 'schema1',
                'userLoginInput': {
                    'email': 'karim.rustom@escape.tech',
                    'password': 'frenchfries'
                }
            }
        },
        'auth': {
            'schema1': {
                'tech': 'graphql',
                'url': 'https://apismxu6skxg-backend.functions.fnc.fr-par.scw.cloud/graphql',
                'method': 'POST',
                'mutation_name': 'login',
                'mutation_field': 'token',
                'options': {
                    'operation': 'mutation',
                    'headers': {
                        'Content-Type': 'application/json'
                    }
                }
            }
        }
    }


@pytest.fixture
def graphql_curl_with_input_object_and_var_response() -> dict:
    """Curl Response."""
    return {
        'users': {
            'user1': {
                'auth': 'schema1',
                'Login': {
                    'email': 'karim.rustom@escape.tech',
                    'password': 'frenchfries'
                }
            }
        },
        'auth': {
            'schema1': {
                'tech': 'graphql',
                'url': 'https://apismxu6skxg-backend.functions.fnc.fr-par.scw.cloud/graphql',
                'method': 'POST',
                'mutation_name': 'login',
                'mutation_field': 'token',
                'options': {
                    'operation': 'mutation',
                    'headers': {
                        'Content-Type': 'application/json'
                    }
                }
            }
        }
    }


@pytest.fixture
def graphql_curl_with_normal_graphql_query_response() -> dict:
    """Curl Response."""
    return {
        'users': {
            'user1': {
                'auth': 'schema1',
                'username': 'jw.anon.5172@gmail.com',
                'password': 'Wj7UxfFTyzgPVM'
            }
        },
        'auth': {
            'schema1': {
                'tech': 'graphql',
                'url': 'https://www.terrang.fr/graphql',
                'method': 'POST',
                'mutation_name': 'authenticateUser',
                'options': {
                    'operation': 'mutation',
                    'headers': {
                        'Content-Type': 'application/json'
                    }
                }
            }
        }
    }


@pytest.fixture
def rest_curl_response() -> dict:
    """Curl Response."""
    return {
        'users': {
            'user1': {
                'auth': 'schema1',
                'email': 'jw.anon.5172@gmail.com',
                'password': 'Wj7UxfFTyzgPVM@'
            }
        },
        'auth': {
            'schema1': {
                'tech': 'rest',
                'url': 'https://auth.console.fauna.com/login',
                'method': 'POST',
                'options': {
                    'headers': {
                        'Content-Type': 'application/json'
                    }
                }
            }
        }
    }


@pytest.fixture
def rest_curl_not_json_response() -> dict:
    """Curl Response."""
    return {
        'users': {
            'user1': {
                'auth': 'schema1',
                'email': 'jw.anon.5172@gmail.com',
                'password': 'Wj7UxfFTyzgPVM@'
            }
        },
        'auth': {
            'schema1': {
                'tech': 'rest',
                'url': 'https://auth.console.fauna.com/login',
                'method': 'POST',
                'options': {
                    'headers': {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }
            }
        }
    }


def test_serialize_headers(auth: dict, users_one_header: dict, users_two_headers: dict) -> None:
    """Test serialize_headers."""

    headers_str = 'Authorization: Bearer 12345'
    headers_list = ['Authorization: Bearer 12345', 'Content-Type: application/json']
    headers_dict = {'Authorization': 'Bearer 12345', 'Content-Type': 'application/json'}

    auths_str, users_str = raw_headers_to_manual(headers_str)

    assert auths_str == auth
    assert users_str == users_one_header

    auths_list, users_list = raw_headers_to_manual(headers_list)

    assert auths_list == auth
    assert users_list == users_two_headers

    auths_dict, users_dict = raw_headers_to_manual(headers_dict)

    assert auths_dict == auth
    assert users_dict == users_two_headers


def test_graphql_curl_with_input_object_and_no_var(
    graphql_curl_with_input_object_and_no_var: str, graphql_curl_with_input_object_and_no_var_response: dict
) -> None:
    """Function that tests if the curl to escaperc works."""

    assert curl_to_escaperc(graphql_curl_with_input_object_and_no_var) == graphql_curl_with_input_object_and_no_var_response


def test_graphql_curl_with_input_object_and_var(graphql_curl_with_input_object_and_var: str, graphql_curl_with_input_object_and_var_response: dict) -> None:
    """Function that tests if the curl to escaperc works."""

    assert curl_to_escaperc(graphql_curl_with_input_object_and_var) == graphql_curl_with_input_object_and_var_response


def test_graphql_curl_with_normal_graphql_query(graphql_curl_with_normal_graphql_query: str, graphql_curl_with_normal_graphql_query_response: dict) -> None:
    """Function that tests if the curl to escaperc works."""

    assert curl_to_escaperc(graphql_curl_with_normal_graphql_query) == graphql_curl_with_normal_graphql_query_response


def test_rest_curl(rest_curl: str, rest_curl_response: dict) -> None:
    """Function that tests if the curl to escaperc works."""

    assert curl_to_escaperc(rest_curl) == rest_curl_response


def test_rest_curl_not_json(rest_curl_not_json: str, rest_curl_not_json_response: dict) -> None:
    """Function that tests if the curl to escaperc works."""

    assert curl_to_escaperc(rest_curl_not_json) == rest_curl_not_json_response


def test_curl_no_data(curl_no_data: str) -> None:
    """Function that tests if the curl to escaperc works."""

    assert curl_to_escaperc(curl_no_data) is None
