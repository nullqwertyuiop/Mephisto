from http import HTTPStatus
from typing import Any

from pydantic import BaseModel


class Response(BaseModel):
    message: str
    status: HTTPStatus = HTTPStatus.OK


class SuccessResponse(Response):
    data: Any | None = None
    message: str = "Success"
    status: HTTPStatus = HTTPStatus.OK


class ErrorResponse(Response):
    message: str = "Error"
    status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
