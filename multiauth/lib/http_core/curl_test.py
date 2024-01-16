from http import HTTPMethod
from typing import Any

import pytest

from multiauth.lib.http_core.curl import parse_curl, parse_headers, parse_scheme
from multiauth.lib.http_core.entities import HTTPCookie, HTTPHeader, HTTPQueryParameter, HTTPRequest, HTTPScheme


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
                    headers=list[HTTPHeader](),
                    query_parameters=list[HTTPQueryParameter](),
                    username=None,
                    password=None,
                    data_json=None,
                    data_text=None,
                    cookies=list[HTTPCookie](),
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
                    headers=list[HTTPHeader](),
                    query_parameters=list[HTTPQueryParameter](),
                    username=None,
                    password=None,
                    data_json=None,
                    data_text=None,
                    cookies=list[HTTPCookie](),
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
                    headers=list[HTTPHeader](),
                    query_parameters=list[HTTPQueryParameter](),
                    username=None,
                    password=None,
                    data_json=None,
                    data_text=None,
                    cookies=list[HTTPCookie](),
                    proxy=None,
                ),
            ),
            (
                'curl -X POST https://example.com -H "Authorization-Code: test-code"',
                HTTPRequest(
                    method=HTTPMethod.POST,
                    host='example.com',
                    scheme=HTTPScheme.HTTPS,
                    headers=[
                        HTTPHeader(name='Authorization-Code', values=['test-code']),
                    ],
                    path='/',
                    query_parameters=list[HTTPQueryParameter](),
                    username=None,
                    password=None,
                    data_json=None,
                    data_text=None,
                    cookies=list[HTTPCookie](),
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
                    headers=[
                        HTTPHeader(name='Authorization-Code', values=['test-code']),
                        HTTPHeader(name='Content-Type', values=['application/json']),
                    ],
                    path='/',
                    query_parameters=list[HTTPQueryParameter](),
                    username=None,
                    password=None,
                    data_json=None,
                    data_text=None,
                    cookies=list[HTTPCookie](),
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
                    headers=list[HTTPHeader](),
                    query_parameters=list[HTTPQueryParameter](),
                    username=None,
                    password=None,
                    cookies=list[HTTPCookie](),
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
                    headers=list[HTTPHeader](),
                    query_parameters=list[HTTPQueryParameter](),
                    username=None,
                    password=None,
                    cookies=list[HTTPCookie](),
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
            (None, []),
            ([], []),
            (['Authorization-Code:test-code'], [HTTPHeader(name='Authorization-Code', values=['test-code'])]),
            (['Authorization-Code:         test-code'], [HTTPHeader(name='Authorization-Code', values=['test-code'])]),
            (['Authorization:Bearer jwt'], [HTTPHeader(name='Authorization', values=['Bearer jwt'])]),
            (['Authorization: Bearer jwt'], [HTTPHeader(name='Authorization', values=['Bearer jwt'])]),
            (
                ['Authorization: Bearer jwt', 'Content-Type: application/json'],
                [
                    HTTPHeader(name='Authorization', values=['Bearer jwt']),
                    HTTPHeader(name='Content-Type', values=['application/json']),
                ],
            ),
        ],
    )
    def test_parse_headers(self, raw_headers: Any, expected: list[HTTPHeader]) -> None:
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
