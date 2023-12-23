import argparse
import sys

from multiauth.revamp.cli.load import load_mulitauth
from multiauth.revamp.helpers.logger import setup_logger


def request_command(args: argparse.Namespace) -> None:
    logger = setup_logger()

    multiauth = load_mulitauth(args)

    logger.info(f'Executing request for user {args.user}')

    result = multiauth.get_http_response(user_name=args.user, step=args.step)
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
