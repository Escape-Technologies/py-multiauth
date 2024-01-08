from typing import Any

from multiauth.helpers.logger import setup_logger
from multiauth.lib.audit.events.base import Event, EventsList
from multiauth.lib.audit.reporters.base import BaseEventsReporter, EventSeverity


def format_str(value: Any) -> str:
    v_str = str(value)

    return v_str.replace('"', '\\"')


def logfmt_from_dict(d: Any, base_attr: str | None = None) -> list[str]:
    attributes: list[str] = []

    if isinstance(d, dict):
        for k, v in d.items():
            attr = f'{base_attr}.{k}' if base_attr else k
            attributes += logfmt_from_dict(v, attr)
    elif isinstance(d, list):
        for i, v in enumerate(d):
            attr = f'{base_attr}.{i}' if base_attr else str(i)
            attributes += logfmt_from_dict(v, attr)
    else:
        attributes.append(f'{base_attr}="{format_str(d)}"')

    return attributes


class RawEventsReporter(BaseEventsReporter):
    def __init__(self, output_path: str | None = None) -> None:
        self.output_path = output_path

    def format(self, event: Event) -> tuple[str, EventSeverity]:
        return ' '.join(logfmt_from_dict(event.model_dump(exclude_none=True))), 'info'

    def report(self, events: EventsList) -> None:
        logger = setup_logger()

        raw_events = [self.format(event) for event in events]

        if self.output_path:
            with open(self.output_path, 'a') as f:
                for raw_event, _ in raw_events:
                    f.write(raw_event)
                    f.write('\n')

            return

        for raw_event, _ in raw_events:
            logger.info(raw_event)
