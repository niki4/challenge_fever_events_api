from __future__ import annotations

from datetime import datetime
from typing import Optional, Union

from fastapi import APIRouter
from fastapi import BackgroundTasks, status
from fastapi.responses import JSONResponse

from app.models import SearchGetResponse
from app.models import SearchGetResponse1, SearchGetResponse2
from app.controllers.search import PartnerEventsController
from app.core.storage import storage

router = APIRouter()


@router.get(
    '/search',
    response_model=SearchGetResponse,
    responses={
        '400': {'model': SearchGetResponse1},
        '500': {'model': SearchGetResponse2},
    },
)
async def search_events(
    starts_at: Optional[datetime] = None, ends_at: Optional[datetime] = None,
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> Union[SearchGetResponse, SearchGetResponse1, SearchGetResponse2]:
    """Lists the available events on a specified time range."""

    if not starts_at or not ends_at:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "400",
                    "message": ("missed required query params "
                                "starts_at or ends_at."),
                },
                "data": None})

    # Verifying in this way we may catch by exception_handler's
    # both non-comparable datetimes and when starts_at later than ends_at.
    assert starts_at <= ends_at, "starts_at datetime later than ends_at"

    # For sake of speed/availability, we will return to user immediately what
    # we have at this moment in the storage, while the latest data update will
    # be processed in a handle_new_events_request() in background task,
    # so the updated data will be available on the next user request.
    # More info: https://fastapi.tiangolo.com/tutorial/background-tasks/

    partner_controller = PartnerEventsController()
    background_tasks.add_task(partner_controller.handle_new_events_request,
                              starts_at, ends_at)

    events_list = storage.get_events(starts_at, ends_at)
    return {
        "data": {
            "events": events_list,
        },
        "error": None,
    }
