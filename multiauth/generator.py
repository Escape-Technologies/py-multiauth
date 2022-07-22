"""Generate authrc from -H or cURL."""

from multiauth.types.main import AuthTech


def serialize_headers_to_manual(headers: dict[str, str] | list[str] | str) -> tuple[dict, dict]:
    """Serialize raw headers in "manual" auth format."""

    headers_dict: dict[str, str] = {}

    if isinstance(headers, str):
        headers = [headers]

    if isinstance(headers, list):

        for header in headers:
            header_split = header.split(':', 1)
            headers_dict[header_split[0].strip()] = header_split[1].strip()

    elif isinstance(headers, dict):
        headers_dict = headers

    auth_name = 'manual_headers'

    auths: dict = {
        auth_name: {
            'tech': AuthTech.MANUAL,
        },
    }

    users: dict = {
        'manual_user': {
            'headers': headers_dict,
            'auth': auth_name
        },
    }

    return auths, users
