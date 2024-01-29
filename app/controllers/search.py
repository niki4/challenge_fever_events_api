"""Partner Events API controller module."""

from datetime import datetime

import httpx
from lxml import etree

from app.core import parsers
from app.core import settings
from app.core.logger import logger
from app.core.storage import BaseStorage
from app.models import PartnerEvent


class PartnerEventsController:
    """Partner API events controller."""

    async def fetch_events_from_partner_api(self):
        """Makes request to event partner API.

        async/await allows not to block server on waiting response and it can go
        and do something else in the meanwhile (like receiving another request).
        More info: https://fastapi.tiangolo.com/async/#async-and-await
        """

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(settings.EVENT_PROVIDER_URL,
                                            timeout=settings.REQUEST_TIMEOUT)
                response.raise_for_status()
            except httpx.RequestError as exc:
                logger.error("An error occurred while requesting %s",
                             exc.request.url)
                return
            except httpx.HTTPStatusError as exc:
                logger.error("Error response %s while requesting %s",
                             exc.response.status_code, exc.request.url)
                return
            return response.content

    async def handle_new_events_request(self, starts_from: datetime,
                                        ends_to: datetime,
                                        storage: BaseStorage):
        """Handles request, parse and then store partner event data."""

        response_content = await self.fetch_events_from_partner_api()
        if response_content is None:
            return

        # Parse the XML response
        xml_tree = etree.fromstring(response_content)
        root = xml_tree.getroottree().getroot()

        # Access specific elements and data
        partner_events_data: list[PartnerEvent | None] = (
            parsers.parse_events_data_from_xml(root))
        logger.debug("partner_events_data from xml: %s", partner_events_data)

        # Filter partner data so that we will store only events between user
        # specified start and end datetime.
        for idx, event in enumerate(partner_events_data):
            if not (starts_from <= event.start and event.end <= ends_to):
                # avoid expensive shift of element
                partner_events_data[idx] = None

        logger.debug("partner_events_data after filter: %s",
                     partner_events_data)

        # then store events in the storage
        if partner_events_data:

            for event in partner_events_data:
                if event is not None:
                    storage.set_event(event)

            logger.info("New events saved in storage.")
