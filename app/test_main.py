"""Tests for main module."""

from datetime import datetime
from unittest.mock import patch

from fastapi.testclient import TestClient

from .main import app, handle_new_partner_events_request
from .models import PartnerEvent
from .core.storage import storage


def test_query_params_missed():
    """Tests that validation_exception_handler catches error when
    starts_at datetime and ends_at datetimes are not provided in query params,
    and returns correctly formed JSON-response.
    """

    client = TestClient(app)
    response = client.get("/search")
    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "400",
                    "message": ("missed required query params "
                                "starts_at or ends_at."),
        },
        "data": None}


def test_query_params__invalid_datetime_format():
    """Tests that validation_exception_handler catches error when
    starts_at datetime and ends_at datetimes are in mixed format,
    and returns correctly formed JSON-response.
    """

    params = {
        "starts_at": "aaa",
        "ends_at": "bbb"
    }

    client = TestClient(app)
    response = client.get("/search", params=params)

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "400",
                    "message": "invalid datetime format",
        },
        "data": None}


def test_query_params__mixing_datetime_types():
    """Tests that generic_exception_handler catches error when
    starts_at datetime and ends_at datetimes are in mixed format,
    and returns correctly formed JSON-response.
    """

    params = {
        "starts_at": "2021-05-01T17:32:28Z",  # Z at the end - it's TZ aware
        "ends_at": "2021-07-21T17:32:28"      # no Z at the end - TZ-naive time
    }

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/search", params=params)

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "500",
                    "message": ("can't compare offset-naive"
                                " and offset-aware datetimes"),
        },
        "data": None}


def test_query_params__end_datetime_earlier_than_start_datetime():
    """Tests that generic_exception_handler catches error when
    end datetime earlier than start datetime and returns correctly
    formed JSON-response.
    """

    params = {
        "starts_at": "2022-05-01T17:32:28Z",
        "ends_at": "2021-07-21T17:32:28Z"
    }

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/search", params=params)

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "500",
                    "message": "starts_at datetime later than ends_at",
        },
        "data": None}


def test_search_events__local_storage_empty():
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
            handle_new_partner_events_request,
            starts_at, ends_at
        )

        assert response.status_code == 200

        assert response.json() == {
            "data": {
                "events": [],
            },
            "error": None,
        }


def test_search_events__local_storage_contains_fetched_events_data():
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

    with patch("fastapi.BackgroundTasks.add_task") as add_task_mock:
        response = client.get("/search", params=params)

        add_task_mock.assert_called_once_with(
            handle_new_partner_events_request,
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
