from multiauth.helpers.logger import setup_logger
from multiauth.lib.audit.events.base import Event, EventSeverity, EventsList
from multiauth.lib.audit.reporters.base import BaseEventsReporter


class fg:
    # black = '\u001b[30m'
    red = '\u001b[31m'
    green = '\u001b[32m'
    yellow = '\u001b[33m'
    # blue = '\u001b[34m'
    # magenta = '\u001b[35m'
    # cyan = '\u001b[36m'
    # white = '\u001b[37m'


class bg:
    red = '\u001b[41m'
    green = '\u001b[42m'
    yellow = '\u001b[43m'
    blue = '\u001b[44m'


class util:
    reset = '\u001b[0m'
    bold = '\u001b[1m'
    underline = '\u001b[4m'
    reverse = '\u001b[7m'


def red(str: str) -> str:
    return f'{fg.red}{str}{util.reset}'


def green(str: str) -> str:
    return f'{fg.green}{str}{util.reset}'


def yellow(str: str) -> str:
    return f'{fg.yellow}{str}{util.reset}'


class ConsoleEventsReporter(BaseEventsReporter):
    def format(self, event: Event) -> tuple[str, EventSeverity]:
        msg = f'{event.timestamp} {event.type:<18} {event.severity or event.default_severity:<8} {event.logline}'

        match (event.severity or event.default_severity):
            case 'info':
                return msg, 'info'
            case 'warning':
                return yellow(msg), 'warning'
            case 'error':
                return red(msg), 'error'
            case 'success':
                return green(msg), 'success'
            case _:
                return msg, 'info'

    def report(self, events: EventsList) -> None:
        logger = setup_logger()
        logger.info('')
        for event in events:
            msg, _ = self.format(event)
            logger.info(msg)
        logger.info('')
