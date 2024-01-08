import sys
from argparse import Namespace

from multiauth.helpers.logger import setup_logger
from multiauth.lib.audit.reporters.base import BaseEventsReporter
from multiauth.lib.audit.reporters.console import ConsoleEventsReporter
from multiauth.lib.audit.reporters.json import JSONEventsReporter
from multiauth.lib.audit.reporters.raw import RawEventsReporter
from multiauth.multiauth import Multiauth


def load_mulitauth(args: Namespace) -> tuple[Multiauth, list[BaseEventsReporter]]:
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

    reporters: list[BaseEventsReporter] = []

    if args.reporters:
        reporter_names = set(args.reporters)
        for reporter_name in reporter_names:
            match reporter_name:
                case 'json':
                    reporters.append(JSONEventsReporter())
                case 'console':
                    reporters.append(ConsoleEventsReporter())
                case 'raw':
                    reporters.append(RawEventsReporter())
                case _:
                    logger.error(f'Unknown reporter will be skipped: {reporter_name}')

    if args.outputs:
        outputs = set(args.outputs)
        for output in outputs:
            if not isinstance(output, str):
                logger.error(f'Unknown output type will be skipped: {output}')
                continue
            if output.endswith('.json'):
                reporters.append(JSONEventsReporter(output_path=output))
            elif output.endswith('.txt'):
                reporters.append(RawEventsReporter(output_path=output))
            else:
                logger.error(f'Unknown output type will be skipped: {output}')

    return multiauth, reporters
