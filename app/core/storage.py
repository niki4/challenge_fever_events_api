"""Data storage module."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from datetime import datetime
import threading
from typing import List
import uuid

from app.core.logger import logger
from app.models import EventSummary
from app.models import PartnerEvent


class BaseStorage(metaclass=ABCMeta):
    """This abstract base class defines the two core methods that any storage
    class must implement: get_events and set_event.

    Any storage class that wants to use the BaseStorage
    interface will need to implement these methods.
    """

    @abstractmethod
    def get_events(self,
                   start_from: datetime,
                   ends_to: datetime) -> List[EventSummary]:
        """Returns list of EventSummary from storage within
        specified start_from and ends_to time range."""
        raise NotImplementedError()

    @abstractmethod
    def set_event(self, event: PartnerEvent):
        """Updates event in storage. Creates new record if need."""
        raise NotImplementedError()


class LocalEventStorage(BaseStorage):
    """Concrete implementation of BaseStorage interface."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, storage_engine=None):
        self._storage = storage_engine or {}

    def get_events(self,
                   start_from: datetime,
                   ends_to: datetime) -> List[EventSummary]:
        """Returns list of EventSummary from local storage within
        specified start_from and ends_to time range.
        """
        result = []

        for event in self._storage.values():
            if start_from <= event["start"] and event["end"] <= ends_to:
                result.append({
                    k: v for (k, v) in event.items() if k not in {
                        "start", "end"}
                })

        logger.debug("LocalEventStorage - get_events - result: %s", result)
        return result

    def set_event(self, event: PartnerEvent):
        """Updates event in local storage. Creates new record if need."""

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


local_event_storage = LocalEventStorage()
