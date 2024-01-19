"""Main app module."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Union

from lxml import etree
import requests

from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core import settings
from app.core.storage import EventStorage
from app.models import PartnerEvent
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
    validation error in custom JSON format."""

    details = exc.errors()
    error_msg = ""
    if details:
        error_msg = details[0]["msg"]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({
            "error": {"code": "400", "message": error_msg or details},
            "data": None}))


def parse_events_data_from_xml(root: etree._Element) -> List[PartnerEvent]:
    """Parses given xml document and returns list of Partner Events."""

    if root.tag != "eventList":
        return []

    events_list = []
    output = root.find("output")
    for base_event in output.findall("base_event"):
        if base_event.attrib["sell_mode"] == "online":
            event = base_event.find("event")

            event_id = event.attrib["event_id"]
            base_event_id = base_event.attrib["base_event_id"]
            base_event_title = base_event.attrib["title"]
            event_start_date = event.attrib["event_start_date"]
            event_end_date = event.attrib["event_end_date"]

            # construct UTC tz-aware datetime objects
            if not event_start_date.endswith("Z"):
                event_start_date += "Z"
            event_start = datetime.fromisoformat(event_start_date)

            if not event_end_date.endswith("Z"):
                event_end_date += "Z"
            event_end = datetime.fromisoformat(event_end_date)

            min_price = min(
                float(zone.attrib["price"]) for zone
                in event.findall("zone"))
            max_price = max(
                float(zone.attrib["price"]) for zone
                in event.findall("zone"))

            partner_event = PartnerEvent(
                id=event_id,
                base_event_id=base_event_id,
                title=base_event_title,
                start=event_start,
                end=event_end,
                min_price=min_price,
                max_price=max_price,
            )
            events_list.append(partner_event)

    return events_list


def fetch_events_from_partner_API(dt_from: datetime, dt_to: datetime):  # TODO: async
    # request from event partner API
    response = requests.get(settings.EVENT_PROVIDER_URL,
                            timeout=settings.DEFAULT_REQUEST_TIMEOUT)

    date_from = dt_from.date()
    date_to = dt_to.date()

    print("date_from:", date_from, "date_to:", date_to, end="\n----\n")

    if response.status_code == 200:
        return response.content
    # TODO: need to return anything if response code is not 200?


def handle_new_partner_events_request(starts_from: datetime, ends_to: datetime):  # TODO: async
    """Requests, parses and then stores partner event data."""
    response_content = fetch_events_from_partner_API(starts_from,  # TODO: await
                                                     ends_to)

    # Parse the XML response
    xml_tree = etree.fromstring(response_content)
    root = xml_tree.getroottree().getroot()

    # Access specific elements and data
    partner_events_data = parse_events_data_from_xml(root)
    print(">> before filter:", partner_events_data)

    # Filter partner data so that we will store only events between user
    # specified start and end datetime.
    for idx, event in enumerate(partner_events_data):
        print("starts_from:", starts_from, "event.start:", event.start,
              "---", "event.end:", event.end, "ends_to:", ends_to, "\n")

        if not (starts_from <= event.start and event.end <= ends_to):
            partner_events_data[idx] = None  # avoid expensive shift of element

    print(">> after filter:", partner_events_data)

    # then store events in the storage
    for event in partner_events_data:
        if event is not None:
            storage.set_event(event)

    print(">>> storage content:")
    from pprint import pprint as pp
    pp(storage)


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
    Lists the available events on a time range
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
