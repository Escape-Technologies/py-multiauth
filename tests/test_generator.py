#pylint: disable=redefined-outer-name, unused-import

"""Test generator."""

from multiauth.generator import serialize_headers_to_manual

from .providers.test_manual_auth import auth, users_one_header, users_two_headers  # noqa


def test_serialize_headers(auth: dict, users_one_header: dict, users_two_headers: dict) -> None:
    """Test serialize_headers."""

    headers_str = 'Authorization: Bearer 12345'
    headers_list = ['Authorization: Bearer 12345', 'Content-Type: application/json']
    headers_dict = {'Authorization': 'Bearer 12345', 'Content-Type': 'application/json'}

    auths_str, users_str = serialize_headers_to_manual(headers_str)

    assert auths_str == auth
    assert users_str == users_one_header

    auths_list, users_list = serialize_headers_to_manual(headers_list)

    assert auths_list == auth
    assert users_list == users_two_headers

    auths_dict, users_dict = serialize_headers_to_manual(headers_dict)

    assert auths_dict == auth
    assert users_dict == users_two_headers
