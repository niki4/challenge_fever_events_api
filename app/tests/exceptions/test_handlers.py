"""Tests for exception handlers."""

from fastapi.testclient import TestClient

from app.main import app


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
