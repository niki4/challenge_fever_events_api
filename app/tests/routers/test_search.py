"""Tests for Search Events routers."""

from datetime import datetime
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.controllers.search import PartnerEventsController


@patch("fastapi.BackgroundTasks.add_task")
@patch("app.routers.search.storage")
@patch.object(PartnerEventsController, "handle_new_events_request")
def test_search_events_router(
        handle_new_events_request_mock, storage_mock, add_task_mock):
    """Tests that /search handler returns correct response."""

    params = {
        "starts_at": "2021-05-01T17:32:28Z",
        "ends_at": "2021-07-21T17:32:28Z"
    }
    client = TestClient(app)
    starts_at = datetime.fromisoformat(params["starts_at"])
    ends_at = datetime.fromisoformat(params["ends_at"])

    storage_mock.get_events.return_value = []

    response = client.get("/search", params=params)

    add_task_mock.assert_called_once_with(
        handle_new_events_request_mock,
        starts_at, ends_at, storage_mock
    )

    assert response.status_code == 200

    assert response.json() == {
        "data": {
            "events": [],
        },
        "error": None,
    }
