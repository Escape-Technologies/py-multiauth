import argparse
import json
from http import HTTPMethod

from multiauth.revamp.configuration import MultiauthConfiguration
from multiauth.revamp.engines.http import HTTPExtraction, HTTPRequestConfiguration, HTTPRequestParameters
from multiauth.revamp.engines.procedure import ProcedureConfiguration
from multiauth.revamp.helpers.logger import setup_logger
from multiauth.revamp.lib.http_core.entities import HTTPHeader, HTTPLocation
from multiauth.revamp.store.injection import TokenInjection
from multiauth.revamp.store.user import Credentials, User


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
                name='example-procedure',
                requests=[
                    HTTPRequestConfiguration(
                        parameters=HTTPRequestParameters(
                            url='https://vampi.tools.escape.tech',
                            method=HTTPMethod.GET,
                        ),
                        extractions=[
                            HTTPExtraction(name='example-extraction', location=HTTPLocation.BODY, key='message'),
                        ],
                    ),
                ],
            ),
        ],
        users=[
            User(
                name='example-user',
                procedure='example-procedure',
                injections=[
                    TokenInjection(
                        location=HTTPLocation.HEADER,
                        key='X-Injected-Header',
                        prefix='Prefixed ',
                        variable='example-extraction',
                    ),
                ],
                credentials=Credentials(
                    headers=[HTTPHeader(name='X-Example-Header', values=['example-value'])],
                ),
            ),
        ],
    )

    with open('.multiauthrc.json', 'w') as f:
        data = configuration.dict()
        if schema_path:
            data['$schema'] = schema_path
        f.write(json.dumps(data, indent=2))
        logger.info(f'Configuration file written at {output_path}')
