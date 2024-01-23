"""Tests for main module."""

from fastapi.testclient import TestClient

from .main import app


def test_missed_query_params__triggers__validation_exception_handler():
    client = TestClient(app)
    response = client.get("/search")
    assert response.status_code == 400
    assert response.json() == {
                "error": {
                    "code": "400",
                    "message": ("Missed required query params"
                                "starts_at or ends_at."),
                },
                "data": None}


def test_server_error__triggers__generic_exception_handler():
    params = {
        "starts_at": "2021-05-01T17:32:28Z",  # Z at the end - it's TZ aware
        "ends_at": "2021-07-21T17:32:28"      # no Z at the end - TZ-naive time
    }
    response = None

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/search", params=params)

    assert response.status_code == 500
    assert response.json() == {
                "error": {
                    "code": "500",
                    "message": ("TypeError(\"can't compare offset-naive"
                                " and offset-aware datetimes\")"),
                },
                "data": None}
