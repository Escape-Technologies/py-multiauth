import argparse

from multiauth.revamp.cli.load import load_mulitauth
from multiauth.revamp.helpers.logger import setup_logger


def request_command(args: argparse.Namespace) -> None:
    logger = setup_logger()

    multiauth, reporters = load_mulitauth(args)

    logger.info(f'Executing request for user {args.user}')

    request, response, events = multiauth.get_http_response(user_name=args.user, step=args.step)

    for reporter in reporters:
        reporter.report(events)
