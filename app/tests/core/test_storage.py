"""Tests for storage layer."""

from datetime import datetime
from unittest.mock import patch

from app.core.storage import local_event_storage as event_storage
from app.models import PartnerEvent


class TestEventStorage:

    # pylint: disable=attribute-defined-outside-init
    def setup_method(self):
        """setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """

        self.event_start = datetime.fromisoformat("2021-05-01T17:32:28Z")
        self.event_end = datetime.fromisoformat("2021-07-21T18:42:38Z")

        self.partner_event = PartnerEvent(
            id="111",
            base_event_id="222",
            title="Test Event 123",
            start=self.event_start,
            end=self.event_end,
            min_price=25,
            max_price=35)
        self.partner_event_uuid = "d4d65b72-2d76-4a20-bfce-dbcdba848146"

        with patch("uuid.uuid4") as uuid4_mock:
            uuid4_mock.return_value = self.partner_event_uuid

            event_storage.set_event(self.partner_event)

            event_key = (self.partner_event.base_event_id,
                         self.partner_event.id)
            # pylint: disable=protected-access
            self.stored_event = event_storage._storage[event_key]

    def test_set_event(self):
        """Tests that LocalEventStorage.set_event() method
        correctly handles saving new event in storage.

        Note that main logic moved to setup_method since we need to reuse
        some code in other tests in this class.
        """

        assert self.stored_event == {
            "id": self.partner_event_uuid,
            "title": "Test Event 123",
            "start_date": "2021-05-01",
            "start_time": "17:32:28",
            "end_date": "2021-07-21",
            "end_time": "18:42:38",
            "min_price": 25.0,
            "max_price": 35.0,
            "start": self.event_start,
            "end": self.event_end,
        }

    def test_get_events(self):
        """Tests that LocalEventStorage.get_event() method
        correctly handles getting events from storage."""

        events = event_storage.get_events(self.event_start, self.event_end)
        assert events == [{
            "id": self.partner_event_uuid,
            "title": "Test Event 123",
            "start_date": "2021-05-01",
            "start_time": "17:32:28",
            "end_date": "2021-07-21",
            "end_time": "18:42:38",
            "min_price": 25.0,
            "max_price": 35.0,
        }]
