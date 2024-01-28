"""Tests for Search Events routers."""

from datetime import datetime
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models import PartnerEvent
from app.core.storage import storage
from app.controllers.search import PartnerEventsController


@patch("fastapi.BackgroundTasks.add_task")
@patch.object(PartnerEventsController, "handle_new_events_request")
def test_search_events__local_storage_empty(
        handle_new_events_request_mock, add_task_mock):
    """Tests that /search handler returns correct response even if
    local storage is empty.
    """

    params = {
        "starts_at": "2021-05-01T17:32:28Z",
        "ends_at": "2021-07-21T17:32:28Z"
    }
    client = TestClient(app)
    starts_at = datetime.fromisoformat(params["starts_at"])
    ends_at = datetime.fromisoformat(params["ends_at"])

    with patch("fastapi.BackgroundTasks.add_task") as add_task_mock:
        response = client.get("/search", params=params)

        add_task_mock.assert_called_once_with(
            handle_new_events_request_mock,
            starts_at, ends_at
        )

        assert response.status_code == 200

        assert response.json() == {
            "data": {
                "events": [],
            },
            "error": None,
        }


@patch("fastapi.BackgroundTasks.add_task")
@patch.object(PartnerEventsController, "handle_new_events_request")
def test_search_events__local_storage_contains_fetched_events_data(
        handle_new_events_request_mock, add_task_mock):
    """Tests that /search handler returns data from local storage that
    satisfies specified starts_at and ends_at time range.
    """

    params = {
        "starts_at": "2021-01-01T17:32:28Z",
        "ends_at": "2021-12-31T17:32:28Z"
    }
    client = TestClient(app)
    starts_at = datetime.fromisoformat(params["starts_at"])
    ends_at = datetime.fromisoformat(params["ends_at"])

    storage.set_event(
        PartnerEvent(  # expected event, satisfied our query param filter
            id="123",
            base_event_id="456",
            title="Test Event 1",
            start=datetime.fromisoformat("2021-05-01T17:32:28Z"),
            end=datetime.fromisoformat("2021-07-21T17:32:28Z"),
            min_price=15,
            max_price=30,
        )
    )
    storage.set_event(
        PartnerEvent(  # event is out of range set in query param filter
            id="7",
            base_event_id="8",
            title="Test Event 2",
            start=datetime.fromisoformat("2022-03-01T12:52:18Z"),
            end=datetime.fromisoformat("2022-04-21T12:52:18Z"),
            min_price=15,
            max_price=30,
        )
    )

    event_key = ("456", "123")  # (event.base_event_id, event.id)
    # pylint: disable=protected-access
    expected_event = storage._storage[event_key]

    response = client.get("/search", params=params)

    add_task_mock.assert_called_once_with(
        handle_new_events_request_mock,
        starts_at, ends_at
    )

    assert response.status_code == 200

    assert response.json() == {
        "data": {
            "events": [
                {
                    "id": expected_event["id"],
                    "title": expected_event["title"],
                    "start_date": expected_event["start_date"],
                    "start_time": expected_event["start_time"],
                    "end_date": expected_event["end_date"],
                    "end_time": expected_event["end_time"],
                    "min_price": expected_event["min_price"],
                    "max_price": expected_event["max_price"],
                },
            ],
        },
        "error": None,
    }
