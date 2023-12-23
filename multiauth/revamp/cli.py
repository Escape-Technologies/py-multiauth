# ruff: noqa:T201

"""Multiauth CLI."""

import argparse
import json
import sys
from datetime import date
from http import HTTPMethod

import pkg_resources

from multiauth.revamp.configuration import (
    MultiauthConfiguration,
)
from multiauth.revamp.engines.http import HTTPExtraction, HTTPRequestConfiguration, HTTPRequestParameters
from multiauth.revamp.engines.procedure import ProcedureConfiguration
from multiauth.revamp.helpers.logger import setup_logger
from multiauth.revamp.lib.http_core.entities import HTTPHeader, HTTPLocation
from multiauth.revamp.multiauth import Multiauth
from multiauth.revamp.store.user import Credentials, TokenInjection, User

__version__ = pkg_resources.get_distribution('py-multiauth').version


# pylint: disable=trailing-whitespace
def cli() -> None:
    """Entry point of the CLI program."""

    print(
        r"""
__________          _____        .__   __  .__   _____          __  .__
\______   \___.__. /     \  __ __|  |_/  |_|__| /  _  \  __ ___/  |_|  |__
 |     ___<   |  |/  \ /  \|  |  \  |\   __\  |/  /_\  \|  |  \   __\  |  \
 |    |    \___  /    Y    \  |  /  |_|  | |  /    |    \  |  /|  | |   Y  \
 |____|    / ____\____|__  /____/|____/__| |__\____|__  /____/ |__| |___|  /
           \/            \/                           \/                 \/
    """,
    )

    print('    Maintainer   https://escape.tech')
    print('    Blog         https://escape.tech/blog')
    print('    Contribute   https://github.com/Escape-Technologies/py-multiauth')
    print('')
    print(f'   (c) 2021 - { date.today().year } Escape Technologies - Version: {__version__}')
    print('\n' * 2)

    logger = setup_logger()

    parser = argparse.ArgumentParser(description='MultiAuth - Multi-Authenticator CLI')
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=__version__,
    )
    parser.add_argument(
        '-f',
        '--file',
        type=str,
        help='Configuration file to validate',
        required=False,
    )
    parser.add_argument(
        '-c',
        '--config',
        type=str,
        help='Inline configuration content to validate',
        required=False,
    )

    subparsers = parser.add_subparsers(dest='command', help='sub-command help')

    subparsers.add_parser('lint', help='Validate the structure of a multiauth configuration')

    init = subparsers.add_parser('init', help='Initialize an empty multiauth configuration file')
    init.add_argument(
        '-o',
        '--output-path',
        type=str,
        help='Path to the file where the configuratio will be written',
        dest='output_path',
        required=False,
    )
    init.add_argument(
        '-s',
        '--schema-path',
        type=str,
        help='Path to the JSON schema to add on top of the generated JSON file',
        dest='schema_path',
        required=False,
    )

    request_parser = subparsers.add_parser('request', help='Execute an authentication request and display the response')
    request_parser.add_argument(
        '-u',
        '--user',
        type=str,
        help='The name of the credentials in the config to use when executing the request',
        required=True,
    )
    request_parser.add_argument(
        '-s',
        '--step',
        type=int,
        help='If multiple requests are defined in the procedure, execute the request at the given step',
        required=False,
        default=0,
    )

    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate a multiauth configuration and display the generated authentications',
    )
    validate_parser.add_argument(
        '-u',
        '--user',
        type=str,
        help='The name of the credentials in the config to use when executing the request',
        required=True,
    )

    args = parser.parse_args()

    if args.command == 'init':
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

    if args.file:
        logger.info(f'Validating configuration file at {args.file}')
        mh = Multiauth.from_file(args.file)
        logger.info('Configuration file is valid.')
    elif args.config:
        logger.info('Validating inline configuration')
        mh = Multiauth.from_json_string(args.config)
        logger.info('Configuration is valid.')
    else:
        logger.error('No configuration provided.')
        sys.exit(1)

    match args.command:
        case 'lint':
            logger.info('Configuration is valid.')

        case 'request':
            logger.info(f'Executing request for user {args.user}')

            result = mh.get_http_response(user_name=args.user, step=args.step)
            if not result:
                logger.error('No response received.')
                sys.exit(1)

            request, response = result
            logger.info('')
            logger.info('Request:')
            logger.info(request)
            logger.info('')
            logger.info('Response:')
            logger.info(response)

        case 'validate':
            logger.info(f'Validating credentials for user {args.user}')

            authentication, records = mh.authenticate(user_name=args.user)

            for i, record in enumerate(records):
                request, response, variables = record
                j = i + 1
                logger.info(f'Request {j}:')
                logger.info('')
                logger.info(request)
                logger.info('')
                logger.info(f'Response {j}:')
                logger.info('')
                logger.info(response)
                logger.info('')
                logger.info(f'Variables after step {j}:')
                for variable in variables:
                    logger.info(variable)
                logger.info('')

            logger.info('')
            logger.info('Authentication:')
            logger.info(authentication)
