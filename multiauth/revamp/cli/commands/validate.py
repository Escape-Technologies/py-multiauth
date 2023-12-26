import argparse

from multiauth.revamp.cli.load import load_mulitauth
from multiauth.revamp.helpers.logger import setup_logger


def validate_command(args: argparse.Namespace) -> None:
    logger = setup_logger()

    multiauth = load_mulitauth(args)

    logger.info(f'Validating credentials for user {args.user}')

    authentication, records, expiration = multiauth.authenticate(user_name=args.user)

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
    logger.info(f'Expiration: {expiration}')
