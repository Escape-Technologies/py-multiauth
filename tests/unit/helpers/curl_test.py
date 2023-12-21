from http import HTTPMethod
from typing import Any

import pytest

from multiauth.helpers.curl import HTTPRequest, HTTPScheme, parse_curl, parse_headers, parse_scheme


class TestHttpRequest:
    @pytest.mark.parametrize(
        ('curl', 'expected'),
        [
            (
                'curl example.com',
                HTTPRequest(
                    method=HTTPMethod.GET,
                    host='example.com',
                    scheme=HTTPScheme.HTTP,
                    path='/',
                    headers={},
                    query_parameters={},
                    username=None,
                    password=None,
                    data_json=None,
                    data_text=None,
                    cookies={},
                    proxy=None,
                ),
            ),
            (
                'curl https://example.com',
                HTTPRequest(
                    method=HTTPMethod.GET,
                    host='example.com',
                    scheme=HTTPScheme.HTTPS,
                    path='/',
                    headers={},
                    query_parameters={},
                    username=None,
                    password=None,
                    data_json=None,
                    data_text=None,
                    cookies={},
                    proxy=None,
                ),
            ),
            (
                'curl -X POST https://example.com',
                HTTPRequest(
                    method=HTTPMethod.POST,
                    host='example.com',
                    scheme=HTTPScheme.HTTPS,
                    path='/',
                    headers={},
                    query_parameters={},
                    username=None,
                    password=None,
                    data_json=None,
                    data_text=None,
                    cookies={},
                    proxy=None,
                ),
            ),
            (
                'curl -X POST https://example.com -H "Authorization-Code: test-code"',
                HTTPRequest(
                    method=HTTPMethod.POST,
                    host='example.com',
                    scheme=HTTPScheme.HTTPS,
                    headers={'Authorization-Code': 'test-code'},
                    path='/',
                    query_parameters={},
                    username=None,
                    password=None,
                    data_json=None,
                    data_text=None,
                    cookies={},
                    proxy=None,
                ),
            ),
            (
                (
                    'curl -X POST https://example.com '
                    '-H "Authorization-Code: test-code" '
                    '-H "Content-Type: application/json"'
                ),
                HTTPRequest(
                    method=HTTPMethod.POST,
                    host='example.com',
                    scheme=HTTPScheme.HTTPS,
                    headers={'Authorization-Code': 'test-code', 'Content-Type': 'application/json'},
                    path='/',
                    query_parameters={},
                    username=None,
                    password=None,
                    data_json=None,
                    data_text=None,
                    cookies={},
                    proxy=None,
                ),
            ),
            (
                'curl -X POST https://example.com -d \'{\"foo\": \"bar\"}\'',
                HTTPRequest(
                    method=HTTPMethod.POST,
                    host='example.com',
                    scheme=HTTPScheme.HTTPS,
                    data_text='{"foo": "bar"}',
                    data_json={'foo': 'bar'},
                    path='/',
                    headers={},
                    query_parameters={},
                    username=None,
                    password=None,
                    cookies={},
                    proxy=None,
                ),
            ),
            (
                'curl -X POST https://example.com -d "{\\\"foo\\\": \\\"bar\\\"}"',
                HTTPRequest(
                    method=HTTPMethod.POST,
                    host='example.com',
                    scheme=HTTPScheme.HTTPS,
                    data_text='{"foo": "bar"}',
                    data_json={'foo': 'bar'},
                    path='/',
                    headers={},
                    query_parameters={},
                    username=None,
                    password=None,
                    cookies={},
                    proxy=None,
                ),
            ),
        ],
    )
    def test_parse_valid_curl(self, curl: str, expected: HTTPRequest) -> None:
        assert parse_curl(curl) == expected


class TestParseHeaders:
    @pytest.mark.parametrize(
        ('raw_headers', 'expected'),
        [
            (None, {}),
            ([], {}),
            (['Authorization-Code:test-code'], {'Authorization-Code': 'test-code'}),
            (['Authorization-Code:         test-code'], {'Authorization-Code': 'test-code'}),
            (['Authorization:Bearer jwt'], {'Authorization': 'Bearer jwt'}),
            (['Authorization: Bearer jwt'], {'Authorization': 'Bearer jwt'}),
            (
                ['Authorization: Bearer jwt', 'Content-Type: application/json'],
                {'Authorization': 'Bearer jwt', 'Content-Type': 'application/json'},
            ),
        ],
    )
    def test_parse_headers(self, raw_headers: Any, expected: dict[str, str]) -> None:
        assert parse_headers(raw_headers) == expected


class TestParseScheme:
    @pytest.mark.parametrize(
        ('raw_scheme', 'expected'),
        [
            ('HTTP', HTTPScheme.HTTP),
            ('http', HTTPScheme.HTTP),
            ('HTTPS', HTTPScheme.HTTPS),
            ('https', HTTPScheme.HTTPS),
        ],
    )
    def test_parse_scheme(self, raw_scheme: Any, expected: HTTPScheme) -> None:
        assert parse_scheme(raw_scheme) == expected
