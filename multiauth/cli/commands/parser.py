import argparse

from multiauth.version import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='MultiAuth - Multi-Authenticator CLI',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
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
        '-r',
        '--reporters',
        type=str,
        action='append',
        choices=['console', 'json', 'raw'],
        default=['console'],
        help='How to write the results output',
        required=False,
    )
    parser.add_argument(
        '-o',
        '--outputs',
        type=str,
        action='append',
        help='Path of files where to write the results. The file extension will be used to determine the output format',
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
