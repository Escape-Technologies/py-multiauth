import abc
import os
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_serializer

EventType = Literal[
    'http_request',
    'http_response',
    'http_failure',
    'extraction',
    'log',
    'injection',
    'procedure_aborted',
    'procedure_finished',
    'procedure_started',
    'selenium_log',
    'selenium_error',
    'procedure_skipped',
]

EventSeverity = Literal['info', 'warning', 'error', 'success', 'debug']


class Event(BaseModel, abc.ABC):
    type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    default_severity: EventSeverity
    severity: EventSeverity | None = Field(default=None)

    @field_serializer('timestamp')
    def serialize_dt(self, timestamp: datetime) -> str:
        return timestamp.isoformat()

    @abc.abstractproperty
    def logline(self) -> str:
        ...


class EventsList(list[Event]):
    name: str
    log_enabled: bool

    def __init__(self, *args: Event) -> None:
        self.log_enabled = os.getenv('MH_DEBUG') == '1'
        super().__init__(args)

    def append(self, event: Event) -> None:
        if self.log_enabled:
            msg = f'{event.timestamp} {event.severity or event.default_severity:<8} {event.type:<18} {event.logline}'
            print(msg)  # noqa: T201
        super().append(event)

    # def extend(self, other):
    #     if isinstance(other, type(self)):
    #         super().extend(other)
    #     else:
    #         super().extend(str(item) for item in other)
