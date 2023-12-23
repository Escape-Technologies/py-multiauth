from pydantic import BaseModel, Field

from multiauth.revamp.lib.http_core.entities import HTTPCookie, HTTPHeader, HTTPLocation, HTTPQueryParameter
from multiauth.revamp.lib.http_core.mergers import merge_cookies, merge_headers, merge_query_parameters
from multiauth.revamp.store.injection import TokenInjection
from multiauth.revamp.store.user import User
from multiauth.revamp.store.variables import AuthenticationVariable


class Authentication(BaseModel):
    headers: list[HTTPHeader] = Field(default_factory=list)
    cookies: list[HTTPCookie] = Field(default_factory=list)
    query_parameters: list[HTTPQueryParameter] = Field(default_factory=list)

    @staticmethod
    def empty() -> 'Authentication':
        return Authentication()

    @staticmethod
    def inject(
        injection: TokenInjection,
        variables: list[AuthenticationVariable],
    ) -> 'Authentication':
        authentication = Authentication.empty()

        if len(variables) == 0:
            return authentication

        variable: AuthenticationVariable | None = None
        if injection.variable is None:
            variable = variables[0]
        else:
            variable = next((v for v in variables if v.name == injection.variable), None)

        if variable is None:
            return authentication

        if injection.location == HTTPLocation.HEADER:
            authentication.headers.append(
                HTTPHeader(
                    name=injection.key,
                    values=[f'{injection.prefix or ""}{variable.value}'],
                ),
            )
        elif injection.location == HTTPLocation.COOKIE:
            authentication.cookies.append(
                HTTPCookie(
                    name=injection.key,
                    values=[f'{injection.prefix or ""}{variable.value}'],
                ),
            )
        elif injection.location == HTTPLocation.QUERY:
            authentication.query_parameters.append(
                HTTPQueryParameter(
                    name=injection.key,
                    values=[f'{injection.prefix or ""}{variable.value}'],
                ),
            )

        return authentication

    @staticmethod
    def from_user_and_variables(
        user: User,
        variables: list[AuthenticationVariable],
    ) -> 'Authentication':
        authentication = Authentication.empty()

        if len(variables) == 0:
            return authentication

        variable = variables[0]

        for injection in user.injections:
            if injection.variable is not None:
                findings = [v for v in variables if v.name == injection.variable]
            if len(findings) == 0:
                return authentication
            variable = findings[0]

            match injection.location:
                case HTTPLocation.HEADER:
                    authentication.headers.append(
                        HTTPHeader(
                            name=injection.key,
                            values=[variable.value],
                        ),
                    )
                case HTTPLocation.COOKIE:
                    authentication.cookies.append(
                        HTTPCookie(
                            name=injection.key,
                            values=[variable.value],
                        ),
                    )
                case HTTPLocation.QUERY:
                    authentication.query_parameters.append(
                        HTTPQueryParameter(
                            name=injection.key,
                            values=[variable.value],
                        ),
                    )
        return authentication

    def __str__(self) -> str:
        authentication_str = ''
        if len(self.headers) > 0:
            authentication_str += 'Headers:\n'
            for header in self.headers:
                authentication_str += f'- {header.name}: {header.str_value}\n'
        else:
            authentication_str += 'No headers\n'

        if len(self.cookies) > 0:
            authentication_str += 'Cookies:\n'
            for cookie in self.cookies:
                authentication_str += f'\t- {cookie.name}: {cookie.str_value}\n'
        else:
            authentication_str += 'No cookies\n'

        if len(self.query_parameters) > 0:
            authentication_str += 'Query Parameters:\n'
            for query_parameter in self.query_parameters:
                authentication_str += f'\t- {query_parameter.name}: {query_parameter.str_value}\n'
        else:
            authentication_str += 'No query parameters\n'

        return authentication_str


def merge_authentications(auth_a: Authentication, auth_b: Authentication) -> Authentication:
    return Authentication(
        headers=merge_headers(auth_a.headers, auth_b.headers),
        cookies=merge_cookies(auth_a.cookies, auth_b.cookies),
        query_parameters=merge_query_parameters(auth_a.query_parameters, auth_b.query_parameters),
    )
