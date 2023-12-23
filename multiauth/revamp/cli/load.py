import sys
from argparse import Namespace

from multiauth.revamp.helpers.logger import setup_logger
from multiauth.revamp.multiauth import Multiauth


def load_mulitauth(args: Namespace) -> Multiauth:
    logger = setup_logger()

    if args.file:
        logger.info(f'Validating configuration file at {args.file}')
        multiauth = Multiauth.from_file(args.file)
        logger.info('Configuration file is valid.')
    elif args.config:
        logger.info('Validating inline configuration')
        multiauth = Multiauth.from_json_string(args.config)
        logger.info('Configuration is valid.')
    else:
        logger.error('No configuration provided.')
        sys.exit(1)

    return multiauth
