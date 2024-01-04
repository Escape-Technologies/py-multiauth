import json

from multiauth.revamp.helpers.logger import setup_logger
from multiauth.revamp.lib.audit.events.base import Event
from multiauth.revamp.lib.audit.reporters.base import BaseEventsReporter, EventSeverity


class JSONEventsReporter(BaseEventsReporter):
    def __init__(self, output_path: str | None = None) -> None:
        self.output_path = output_path

    def format(self, event: Event) -> tuple[str, EventSeverity]:
        return event.model_dump_json(indent=2), 'info'

    def report(self, events: list[Event]) -> None:
        logger = setup_logger()

        if self.output_path:
            with open(self.output_path, 'w') as f:
                events_json = [event.model_dump() for event in events]
                f.write(json.dumps(events_json, indent=2))
            return

        for event in events:
            json_event, _ = self.format(event)
            logger.info(json_event)
