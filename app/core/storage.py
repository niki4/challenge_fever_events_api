"""Data storage module."""

from __future__ import annotations

from datetime import datetime

from typing import List
import uuid

from app.core.logger import logger
from app.models import EventSummary
from app.models import PartnerEvent


class EventStorage:
    def __init__(self, storage_engine=None):
        self._storage = storage_engine or {}

    def get_events(self,
                   start_from: datetime,
                   ends_to: datetime) -> List[EventSummary]:
        """Returns list of EventSummary from storage within
        specified start_from and ends_to time range.
        """
        result = []

        for event in self._storage.values():
            if start_from <= event["start"] and event["end"] <= ends_to:
                result.append({
                    k: v for (k, v) in event.items() if k not in ["start, end"]
                })

        logger.debug("EventStorage - get_events - result: %s", result)
        return result

    def set_event(self, event: PartnerEvent):
        """Updates event in storage. Creates new record if need."""

        event_key = (event.base_event_id, event.id)
        if event_key not in self._storage:
            self._storage[event_key] = {
                "id": str(uuid.uuid4()),
                "title": event.title,
            }

        # Update event with latest known values
        self._storage[event_key].update({
            "start_date": str(event.start.date()),  # faster than .strftime
            "start_time": str(event.start.time()),
            "end_date": str(event.end.date()),
            "end_time": str(event.end.time()),
            "min_price": event.min_price,
            "max_price": event.max_price,
            "start": event.start,
            "end": event.end,
        })


storage = EventStorage()
