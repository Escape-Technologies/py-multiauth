import argparse

from multiauth.cli.load import load_mulitauth
from multiauth.helpers.logger import setup_logger


def validate_command(args: argparse.Namespace) -> None:
    logger = setup_logger()

    multiauth, reporters = load_mulitauth(args)

    logger.info(f'Validating credentials for user {args.user}')

    authentication, events, _ = multiauth.authenticate(user_name=args.user)

    for reporter in reporters:
        reporter.report(events)

    logger.info(f'Executed procedure for user {args.user}')
    logger.info(authentication)
