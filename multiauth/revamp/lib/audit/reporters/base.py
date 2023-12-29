import abc
import logging

from multiauth.revamp.helpers import logger
from multiauth.revamp.lib.audit.events.base import Event, EventSeverity


class BaseEventsReporter(abc.ABC):
    logger: logging.Logger

    def __init__(self) -> None:
        self.logger = logger.setup_logger()

    @abc.abstractmethod
    def format(self, event: Event) -> tuple[str, EventSeverity]:
        ...

    def report(self, events: list[Event]) -> None:
        for event in events:
            msg, severity = self.format(event)
            match severity:
                case 'info':
                    self.logger.info(msg)
                case 'warning':
                    self.logger.warning(msg)
                case 'error':
                    self.logger.error(msg)
                case 'success':
                    self.logger.info(msg)