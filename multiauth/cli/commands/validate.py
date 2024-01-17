import argparse

from multiauth.cli.load import load_mulitauth
from multiauth.helpers.logger import setup_logger


def exit_with_error(message: str) -> None:
    print(message)  # noqa: T201
    exit(1)


def validate_command(args: argparse.Namespace) -> None:
    logger = setup_logger()

    multiauth, reporters = load_mulitauth(args)

    logger.info(f'Validating credentials for user {args.user}')

    try:
        authentication, events, expiration, error = multiauth.authenticate(user_name=args.user)
        for reporter in reporters:
            reporter.report(events)
    except Exception as e:
        exit_with_error(f'Unexpected error while authenticating user {args.user}: {e}')

    if error is not None:
        exit_with_error(f'Error while authenticating user {args.user}: {error}')

    logger.info(f'Executed procedure for user {args.user}')
    logger.info(authentication)
