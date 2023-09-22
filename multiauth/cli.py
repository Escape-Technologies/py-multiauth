"""Multiauth CLI."""

import argparse
from datetime import date

import pkg_resources

from multiauth.main import MultiAuth
from multiauth.utils import setup_logger

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
        'validate',
        help='Validate a configuration file',
    )
    parser.add_argument(
        '-f',
        '--file',
        help='Configuration file to validate',
        required=False,
    )

    args = parser.parse_args()

    if args.validate:
        if not args.file:
            logger.info('No configuration file provided.')

        try:
            auth = MultiAuth(authrc=args.file)
            for user in auth.users:
                auth.authenticate(user)

            logger.info('Configuration file is valid.')

            for user in auth.users:
                logger.info(f'User: {user} | Headers: {auth.headers[user]}')

        except Exception as e:
            logger.error('Invalid configuration file.')
            raise e
