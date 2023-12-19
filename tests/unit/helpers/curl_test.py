from typing import Any

import pytest

from multiauth.helpers.curl import HttpRequest, HttpScheme, parse_headers, parse_scheme


class TestHttpRequest:
    @pytest.mark.parametrize(
        ('curl', 'expected'),
        [
            ('curl example.com', HttpRequest(method='GET', host='example.com', scheme=HttpScheme.HTTP)),
            ('curl https://example.com', HttpRequest(method='GET', host='example.com', scheme=HttpScheme.HTTPS)),
            (
                'curl -X POST https://example.com',
                HttpRequest(method='POST', host='example.com', scheme=HttpScheme.HTTPS),
            ),
            (
                'curl -X POST https://example.com -H "Authorization-Code: test-code"',
                HttpRequest(
                    method='POST',
                    host='example.com',
                    scheme=HttpScheme.HTTPS,
                    headers={'Authorization-Code': 'test-code'},
                ),
            ),
            (
                (
                    'curl -X POST https://example.com '
                    '-H "Authorization-Code: test-code" '
                    '-H "Content-Type: application/json"'
                ),
                HttpRequest(
                    method='POST',
                    host='example.com',
                    scheme=HttpScheme.HTTPS,
                    headers={'Authorization-Code': 'test-code', 'Content-Type': 'application/json'},
                ),
            ),
            (
                'curl -X POST https://example.com -d \'{\"foo\": \"bar\"}\'',
                HttpRequest(
                    method='POST',
                    host='example.com',
                    scheme=HttpScheme.HTTPS,
                    data='{"foo": "bar"}',
                    json={'foo': 'bar'},
                ),
            ),
            (
                'curl -X POST https://example.com -d "{\\\"foo\\\": \\\"bar\\\"}"',
                HttpRequest(
                    method='POST',
                    host='example.com',
                    scheme=HttpScheme.HTTPS,
                    data='{"foo": "bar"}',
                    json={'foo': 'bar'},
                ),
            ),
        ],
    )
    def test_parse_valid_curl(self, curl: str, expected: HttpRequest) -> None:
        assert HttpRequest.from_curl(curl) == expected


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
            ('HTTP', HttpScheme.HTTP),
            ('http', HttpScheme.HTTP),
            ('HTTPS', HttpScheme.HTTPS),
            ('https', HttpScheme.HTTPS),
        ],
    )
    def test_parse_scheme(self, raw_scheme: Any, expected: HttpScheme) -> None:
        assert parse_scheme(raw_scheme) == expected
