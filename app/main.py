"""Main app module."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Union

from fastapi import FastAPI

from models import SearchGetResponse, SearchGetResponse1, SearchGetResponse2


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


@app.get(
    '/search',
    response_model=SearchGetResponse,
    responses={
        '400': {'model': SearchGetResponse1},
        '500': {'model': SearchGetResponse2},
    },
)
def search_events(
    starts_at: Optional[datetime] = None, ends_at: Optional[datetime] = None
) -> Union[SearchGetResponse, SearchGetResponse1, SearchGetResponse2]:
    """
    Lists the available events on a time range
    """
    if not starts_at or not ends_at:
        return {
            "data": None,
            "error": {
                "code": "400",
                "message": "Missed required query params starts_at or ends_at."
            }}

    # TODO: return actual data from partner API
    return {
        "data": {
            "events": [
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "title": "string",
                    "start_date": "2024-01-06",
                    "start_time": "22:38:19",
                    "end_date": "2024-01-06",
                    "end_time": "14:45:15",
                    "min_price": 0,
                    "max_price": 0
                },
            ],
        },
        "error": None,
    }
