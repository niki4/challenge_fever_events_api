"""Data storage module."""

from __future__ import annotations

from datetime import datetime
from typing import List
import uuid

from app.models import EventSummary
from app.models import PartnerEvent


class EventStorage:
    def __init__(self, storage_engine=None):
        self.storage = storage_engine or {}

    def get_events(self,
                   dt_from: datetime,
                   dt_to: datetime) -> List[EventSummary]:
        # "start_date": str(event.start.date()),  # faster than .strftime
        # "start_time": str(event.start.time()),
        # "end_date": str(event.end.date()),
        # "end_time": str(event.end.time()),
        return [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "title": "string",
                "start_date": "2024-01-06",
                "start_time": "22:38:19",
                "end_date": "2024-01-06",
                "end_time": "14:45:15",
                "min_price": 0,
                "max_price": 0
            },
        ]

    def set_event(self, event: PartnerEvent):
        """Updates event in storage. Creates new record if need."""
        event_time = (event.start, event.end)
        if event_time not in self.storage:
            self.storage[event_time] = {}

        event_key = event.base_event_id + "_" + event.id

        events = self.storage[event_time]
        if event_key not in events:
            events[event_key] = {
                "id": str(uuid.uuid4()),
                "title": event.title,
            }
        events[event_key].update({
            "start_date": str(event.start.date()),  # faster than .strftime
            "start_time": str(event.start.time()),
            "end_date": str(event.end.date()),
            "end_time": str(event.end.time()),
            "min_price": event.min_price,
            "max_price": event.max_price,
        })
