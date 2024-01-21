"""Main app module."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Union

from lxml import etree
import requests

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core import parsers
from app.core import settings
from app.core.logger import logger
from app.core.storage import EventStorage
from app.models import SearchGetResponse
from app.models import SearchGetResponse1, SearchGetResponse2


app = FastAPI(
    title='Fever Providers API',
    version='1.0.0',
    servers=[
        {
            'description': 'SwaggerHub API Auto Mocking',
            'url': 'https://virtserver.swaggerhub.com/luis-pintado-feverup/backend-test/1.0.0',
        }
    ],
)


storage = EventStorage()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
        request: Request, exc: RequestValidationError) -> SearchGetResponse1:
    """Overrides default request params validator and returns
    request validation error in custom JSON format."""

    details = exc.errors()
    error_msg = ""
    if details:
        error_msg = details[0]["msg"]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({
            "error": {"code": "400", "message": error_msg or details},
            "data": None}))


@app.exception_handler(500)
async def generic_exception_handler(
        request: Request, exc: Exception) -> SearchGetResponse2:
    """Overrides default generic handler for Server Errors and returns
    request validation error in custom JSON format."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({
            "error": {"code": "500", "message": repr(exc)},
            "data": None}))


def fetch_events_from_partner_api(dt_from: datetime, dt_to: datetime):  # TODO: async
    """Makes request to event partner API."""
    response = requests.get(settings.EVENT_PROVIDER_URL,
                            timeout=settings.DEFAULT_REQUEST_TIMEOUT)

    if response.status_code == 200:
        return response.content

    logger.info("Request to %s return response with status code %s",
                settings.EVENT_PROVIDER_URL, response.status_code)


def handle_new_partner_events_request(starts_from: datetime, ends_to: datetime):  # TODO: async
    """Handles request, parse and then store partner event data."""
    response_content = fetch_events_from_partner_api(starts_from,  # TODO: await
                                                     ends_to)

    # Parse the XML response
    xml_tree = etree.fromstring(response_content)
    root = xml_tree.getroottree().getroot()

    # Access specific elements and data
    partner_events_data = parsers.parse_events_data_from_xml(root)
    logger.debug("partner_events_data from xml: %s", partner_events_data)

    # Filter partner data so that we will store only events between user
    # specified start and end datetime.
    for idx, event in enumerate(partner_events_data):
        if not (starts_from <= event.start and event.end <= ends_to):
            partner_events_data[idx] = None  # avoid expensive shift of element

    logger.debug("partner_events_data after filter: %s", partner_events_data)

    # then store events in the storage
    for event in partner_events_data:
        if event is not None:
            storage.set_event(event)
    logger.info("New events saved in storage.")


@app.get(
    '/search',
    response_model=SearchGetResponse,
    responses={
        '400': {'model': SearchGetResponse1},
        '500': {'model': SearchGetResponse2},
    },
)
def search_events(
    starts_at: Optional[datetime] = None, ends_at: Optional[datetime] = None,
) -> Union[SearchGetResponse, SearchGetResponse1, SearchGetResponse2]:
    """
    Lists the available events on a specified time range.
    """
    if not starts_at or not ends_at:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "400",
                    "message": ("Missed required query params"
                                "starts_at or ends_at."),
                },
                "data": None})

    handle_new_partner_events_request(starts_at, ends_at)

    # for sake of speed/availability, we can return to user immediately what
    # we have at this moment in the storage, so the updated data will be
    # available on the next user request.
    events_list = storage.get_events(starts_at, ends_at)
    return {
        "data": {
            "events": events_list,
        },
        "error": None,
    }
