import argparse
import json
from http import HTTPMethod

from multiauth.configuration import MultiauthConfiguration
from multiauth.helpers.logger import setup_logger
from multiauth.lib.http_core.entities import HTTPHeader, HTTPLocation
from multiauth.lib.procedure import ProcedureConfiguration, ProcedureName
from multiauth.lib.runners.http import HTTPBodyExtraction, HTTPRequestParameters, HTTPRunnerConfiguration
from multiauth.lib.store.injection import TokenInjection
from multiauth.lib.store.user import Credentials, User, UserAuthentication, UserName
from multiauth.lib.store.variables import AuthenticationVariable, VariableName


def init_command(args: argparse.Namespace) -> None:
    logger = setup_logger()

    output_path = args.output_path or '.multiauthrc'
    schema_path = args.schema_path

    logger.info(f'Generating an empty .multiauthrc file at path {output_path}')
    if schema_path:
        logger.info(f'Using schema at path {schema_path}')
    logger.info('Please refer to the documentation for more information on how to configure it.')

    configuration = MultiauthConfiguration(
        procedures=[
            ProcedureConfiguration(
                name=ProcedureName('example-procedure'),
                operations=[
                    HTTPRunnerConfiguration(
                        parameters=HTTPRequestParameters(
                            url='https://vampi.tools.escape.tech',
                            method=HTTPMethod.GET,
                            headers=[
                                HTTPHeader(
                                    name='X-Example-Header-From-User-Variable',
                                    values=['{{ example-user-variable }}'],
                                ),
                            ],
                        ),
                        extractions=[
                            HTTPBodyExtraction(name=VariableName('example-extraction'), key='message'),
                        ],
                    ),
                    HTTPRunnerConfiguration(
                        parameters=HTTPRequestParameters(
                            url='https://vampi.tools.escape.tech',
                            method=HTTPMethod.GET,
                            headers=[
                                HTTPHeader(
                                    name=VariableName('X-Example-Header-Extracted'),
                                    values=['{{ example-extraction }}'],
                                ),
                            ],
                        ),
                        extractions=[],
                    ),
                ],
            ),
        ],
        users=[
            User(
                name=UserName('example-user'),
                authentication=UserAuthentication(
                    procedure='example-procedure',
                    injections=[
                        TokenInjection(
                            location=HTTPLocation.HEADER,
                            key='X-Injected-Header',
                            prefix='Prefixed ',
                            variable='example-extraction',
                        ),
                    ],
                ),
                variables=[
                    AuthenticationVariable(
                        name=VariableName('example-user-variable'),
                        value='example-user-value',
                    ),
                ],
                credentials=Credentials(),
            ),
        ],
    )

    with open('.multiauthrc.json', 'w') as f:
        data = configuration.dict()
        if schema_path:
            data['$schema'] = schema_path
        f.write(json.dumps(data, indent=2))
        logger.info(f'Configuration file written at {output_path}')
