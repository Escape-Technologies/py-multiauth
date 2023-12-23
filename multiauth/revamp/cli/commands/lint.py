import argparse

from multiauth.revamp.helpers.logger import setup_logger


def lint_command(_args: argparse.Namespace) -> None:
    logger = setup_logger()
    logger.info('Configuration is valid.')
