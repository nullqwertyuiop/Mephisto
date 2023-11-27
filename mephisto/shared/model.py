from typing import Literal

from pydantic import BaseModel


class GenericResponse(BaseModel):
    """Generic response."""

    code: int
    """ Response code. """
    type: str
    """ Response type. """
    message: str
    """ Response message. """
    data: dict | None = None
    """ Response data. """


class GenericErrorResponse(GenericResponse):
    """Generic error response."""

    type: Literal["error"]
    """ Response type. """


class GenericSuccessResponse(GenericResponse):
    """Generic success response."""

    type: Literal["success"]
    """ Response type. """
