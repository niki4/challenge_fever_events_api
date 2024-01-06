"""Models for request and response structures."""

from __future__ import annotations

from datetime import date, time
from typing import Any, Dict, List
from uuid import UUID

from pydantic import BaseModel, Field


class EventSummary(BaseModel):
    id: UUID = Field(..., description='Identifier for the plan (UUID)')
    title: str = Field(..., description='Title of the plan')
    start_date: date = Field(
        ..., description='Date when the event starts in local time'
    )
    start_time: time = Field(
        ..., description='Time when the event starts in local time',
        example='22:38:19'
    )
    end_date: date = Field(
        ..., description='Date when the event ends in local time')
    end_time: time = Field(
        ..., description='Time when the event ends in local time',
        example='14:45:15'
    )
    min_price: float = Field(
        ..., description='Min price from all the available tickets'
    )
    max_price: float = Field(
        ..., description='Min price from all the available tickets'
    )


class Error(BaseModel):
    code: str = Field(..., description='Error code')
    message: str = Field(..., description='Detail of the error')


class SearchGetResponse1(BaseModel):
    error: Error
    data: Dict[str, Any] | None = None


class Error1(BaseModel):
    code: str = Field(..., description='Error code')
    message: str = Field(..., description='Detail of the error')


class SearchGetResponse2(BaseModel):
    error: Error1
    data: Dict[str, Any] | None = None


class EventList(BaseModel):
    events: List[EventSummary]


class SearchGetResponse(BaseModel):
    data: EventList | None
    error: Dict[str, Any] | None
