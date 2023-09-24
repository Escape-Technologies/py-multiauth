# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring

import logging

import pytest

from multiauth.main import load_authrc


class TestAuthrcLoader:
    logger: logging.Logger

    def setup(self) -> None:
        self.logger = logging.getLogger(__name__)

    def test_load_authrc_from_file(self) -> None:
        res = load_authrc(self.logger, 'tests/fixtures/.authrc-example')

        assert len(res) == 2
        assert res[0] == {
            'schema1': {
                'tech': 'graphql',
                'url': 'http://example.com/graphql',
                'mutation_name': 'authentification',
                'mutation_field': 'token',
                'method': 'POST',
            },
        }
        assert res[1] == {
            'user1': {'auth': 'schema1', 'username': 'user1', 'password': 'pwd1'},
            'user2': {'auth': 'schema1', 'username': 'user2', 'password': 'pwd2'},
        }

    def test_load_authrc_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv('AUTHRC', 'tests/fixtures/.authrc-example')

        res = load_authrc(self.logger)

        assert len(res) == 2
        assert res[0] == {
            'schema1': {
                'tech': 'graphql',
                'url': 'http://example.com/graphql',
                'mutation_name': 'authentification',
                'mutation_field': 'token',
                'method': 'POST',
            },
        }
        assert res[1] == {
            'user1': {'auth': 'schema1', 'username': 'user1', 'password': 'pwd1'},
            'user2': {'auth': 'schema1', 'username': 'user2', 'password': 'pwd2'},
        }

    def headers_shorthand(self) -> None:
        res = load_authrc(self.logger, 'tests/fixtures/.authrc-shorthand-example')

        assert len(res) == 2
        assert res[0] == {'default_schema': {'tech': 'manual'}}
        assert res[1] == {
            'default_user': {
                'auth': 'default_schema',
                'headers': {'header1': 'value1', 'header2': 'value2'},
            },
        }
