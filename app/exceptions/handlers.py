"""App exceptions handlers."""

from fastapi import Request
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.models import SearchGetResponse1
from app.models import SearchGetResponse2


async def generic_exception_handler(
        request: Request, exc: Exception) -> SearchGetResponse2 | JSONResponse:
    """Overrides default generic handler for Server Errors and returns
    request validation error in custom JSON format.
    """

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({
            "error": {"code": "500", "message": str(exc)},
            "data": None}))


async def validation_exception_handler(
        request: Request, exc: RequestValidationError) -> SearchGetResponse1 | JSONResponse:
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
