import argparse

from multiauth.revamp.version import __version__


def build_parser() -> argparse.ArgumentParser:
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

    return parser