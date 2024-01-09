from multiauth.lib.http_core.entities import HTTPCookie


def test_cookie_serialization() -> None:
    cookie = HTTPCookie(name='mycookie', values=['value1', 'value2'])
    assert cookie.str_value == 'value1%2Cvalue2'


def test_cookies_serialization() -> None:
    cookies = [
        HTTPCookie(name='mycookie', values=['value1', 'value2']),
        HTTPCookie(name='mycookie2', values=['value3', 'value4']),
    ]
    assert HTTPCookie.serialize(cookies) == 'mycookie=value1%2Cvalue2; mycookie2=value3%2Cvalue4'
