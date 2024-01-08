import json

from multiauth.helpers.logger import setup_logger
from multiauth.lib.audit.events.base import Event, EventsList
from multiauth.lib.audit.reporters.base import BaseEventsReporter, EventSeverity


class JSONEventsReporter(BaseEventsReporter):
    def __init__(self, output_path: str | None = None) -> None:
        self.output_path = output_path

    def format(self, event: Event) -> tuple[str, EventSeverity]:
        return event.model_dump_json(indent=2), 'info'

    def report(self, events: EventsList) -> None:
        logger = setup_logger()

        if self.output_path:
            with open(self.output_path, 'w') as f:
                events_json = [event.model_dump() for event in events]
                f.write(json.dumps(events_json, indent=2))
            return

        for event in events:
            json_event, _ = self.format(event)
            logger.info(json_event)
