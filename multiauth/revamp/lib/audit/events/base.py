import abc
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
]

EventSeverity = Literal['info', 'warning', 'error', 'success']


class Event(BaseModel, abc.ABC):
    type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    default_severity: EventSeverity
    severity: EventSeverity | None = Field(default=None)

    @field_serializer('timestamp')
    def serialize_dt(self, timestamp: datetime) -> str:
        return timestamp.isoformat()
