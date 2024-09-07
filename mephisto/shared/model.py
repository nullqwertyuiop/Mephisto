from http import HTTPStatus
from typing import Any

from pydantic import BaseModel


class GenericResponse(BaseModel):
    """Generic response."""

    code: HTTPStatus = HTTPStatus.OK
    """ Response code. """

    type: str
    """ Response type. """

    message: str
    """ Response message. """

    data: Any = None
    """ Response data. """


class GenericErrorResponse(GenericResponse):
    """Generic error response."""

    code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    """ Response code. """

    type: str = "error"
    """ Response type. """


class GenericSuccessResponse(GenericResponse):
    """Generic success response."""

    code: HTTPStatus = HTTPStatus.OK
    """ Response code. """

    type: str = "success"
    """ Response type. """
