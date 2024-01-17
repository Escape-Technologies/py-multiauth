from pydantic import Field

from multiauth.helpers.base_model import StrictBaseModel
from multiauth.lib.audit.events.base import EventsList
from multiauth.lib.audit.events.events import InjectedVariableEvent
from multiauth.lib.http_core.entities import HTTPCookie, HTTPHeader, HTTPLocation, HTTPQueryParameter
from multiauth.lib.store.authentication import Authentication
from multiauth.lib.store.variables import AuthenticationVariable


class TokenInjection(StrictBaseModel):
    location: HTTPLocation = Field(description='The location of the HTTP request where the token should be injected')
    key: str = Field(
        description=(
            'The key to use for the injected token. Its usage depends on the location. For headers, cookies,'
            'and query parameters, this key describes the name of the header, cookie or query parameter. For a body '
            'location, the key is the field where the token should be injected within the request bodies'
        ),
        examples=['Authorization', 'sessionId', 'access_token'],
    )
    prefix: str | None = Field(
        default=None,
        description='A prefix to prepend to the token before it is injected',
        examples=['Bearer '],
    )
    variable: str | None = Field(
        default=None,
        description=(
            "The name of a variable to retrieve to create the token's value. If not provided, "
            'the token will be infered as the first successful extraction of the procedure'
        ),
    )

    @staticmethod
    def examples() -> list['TokenInjection']:
        return [
            TokenInjection(
                variable='token',
                key='Authorization',
                location=HTTPLocation.HEADER,
                prefix='Bearer ',
            ),
        ]

    def inject(
        self,
        variables: list[AuthenticationVariable],
    ) -> tuple[Authentication, EventsList]:
        authentication = Authentication.empty()
        events = EventsList()

        if len(variables) == 0:
            return authentication, events

        variable: AuthenticationVariable | None = None
        if self.variable is None:
            variable = variables[0]
        else:
            variable = next((v for v in variables if v.name == self.variable), None)

        if variable is None:
            return authentication, events

        if self.location == HTTPLocation.HEADER:
            if self.prefix:
                header = HTTPHeader(
                    name=self.key,
                    values=[f'{self.prefix.strip()} {variable.value}'],
                )
            else:
                header = HTTPHeader(
                    name=self.key,
                    values=[variable.value],
                )
            authentication.headers.append(header)
            events.append(InjectedVariableEvent(variable=variable, location=HTTPLocation.HEADER, target=self.key))
        elif self.location == HTTPLocation.COOKIE:
            cookie = HTTPCookie(
                name=self.key,
                values=[f'{self.prefix or ""}{variable.value}'],
            )
            authentication.cookies.append(cookie)
            events.append(InjectedVariableEvent(variable=variable, location=HTTPLocation.COOKIE, target=self.key))
        elif self.location == HTTPLocation.QUERY:
            query_parameter = HTTPQueryParameter(
                name=self.key,
                values=[f'{self.prefix or ""}{variable.value}'],
            )
            authentication.query_parameters.append(query_parameter)
            events.append(InjectedVariableEvent(variable=variable, location=HTTPLocation.QUERY, target=self.key))
        return authentication, events
