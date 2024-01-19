"""Data parsers module."""

from __future__ import annotations

from datetime import datetime
from typing import List

from lxml import etree

from app.models import PartnerEvent


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
