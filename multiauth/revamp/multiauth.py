import json
from typing import Any

from multiauth.revamp.configuration import (
    MultiauthConfiguration,
)
from multiauth.revamp.engines.procedure import Procedure
from multiauth.revamp.lib.http_core.entities import HTTPRequest, HTTPResponse
from multiauth.revamp.store.authentication import Authentication
from multiauth.revamp.store.user import User
from multiauth.revamp.store.variables import AuthenticationVariable


class Multiauth:
    configuration: MultiauthConfiguration
    procedures: dict[str, Procedure]
    users: dict[str, User]

    def __init__(self, configuration: MultiauthConfiguration, seed: list[HTTPResponse] | None = None) -> None:
        seed = seed or []

        self.configuration = configuration
        self.procedures = {}
        self.users = {}

        for procedure_configuration in configuration.procedures:
            self.procedures[procedure_configuration.name] = Procedure(procedure_configuration)
        for user in configuration.users:
            self.users[user.name] = user

        for procedure in self.procedures.values():
            procedure.load_responses(seed)

    def _get_user(self, user_name: str) -> User:
        user = self.users.get(user_name)
        if not user:
            raise ValueError(f'Invalid user name. User `{user_name}` not registered in users list.')
        return user

    def _get_procedure(
        self,
        user_name: str,
    ) -> Procedure:
        user = self.users.get(user_name)
        if not user:
            raise ValueError(
                f'Invalid user name. User `{user_name}` not registered in users list.',
            )

        procedure_name = user.procedure
        procedure = self.procedures.get(procedure_name)

        if not procedure:
            raise ValueError(
                (
                    f'Invalid procedure tech. Provider `{procedure_name}` has an'
                    'invalid tech {procedure_configuration.tech}.'
                ),
            )

        return procedure

    def get_http_response(self, user_name: str, step: int) -> tuple[HTTPRequest, HTTPResponse] | None:
        user = self._get_user(user_name)
        procedure = self._get_procedure(user_name)
        return procedure.request(user, step)

    def extract_variables(self, user_name: str, response: HTTPResponse, step: int) -> list[AuthenticationVariable]:
        procedure = self._get_procedure(user_name)
        return procedure.extract(response, step)

    def authenticate(
        self,
        user_name: str,
    ) -> tuple[Authentication, list[tuple[HTTPRequest, HTTPResponse, list[AuthenticationVariable]]]]:
        user = self._get_user(user_name)
        procedure = self._get_procedure(user_name)

        return procedure.authenticate(user)

    @staticmethod
    def from_json_string(raw_configuration_string: str) -> 'Multiauth':
        configuration = MultiauthConfiguration.model_validate_json(raw_configuration_string)
        return Multiauth(configuration)

    @staticmethod
    def from_file(path: str) -> 'Multiauth':
        with open(path) as f:
            raw_configuration = f.read()
        return Multiauth.from_json_string(raw_configuration)

    @staticmethod
    def from_any(raw_configuration: Any) -> 'Multiauth':
        return Multiauth.from_json_string(json.dumps(raw_configuration))
