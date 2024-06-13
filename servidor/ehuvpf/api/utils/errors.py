from __future__ import annotations
from http import HTTPStatus

from django.http import JsonResponse

class ErrorKind:
    FORBIDDEN = 0
    BAD_REQUEST = 1
    UNPROCESSABLE = 2

    def __init__(self, id: int) -> None:
        self.id = id

    def forbidden() -> ErrorKind:
        return ErrorKind(ErrorKind.FORBIDDEN)

    def bad_request() -> ErrorKind:
        return ErrorKind(ErrorKind.BAD_REQUEST)

    def unprocessable() -> ErrorKind:
        return ErrorKind(ErrorKind.UNPROCESSABLE)

class ApiError:
    def __init__(self, endpoint: str, reason: str, error_kind: ErrorKind) -> None:
        self.endpoint = endpoint
        self.reason = reason
        self.error_kind = error_kind

    def to_response(self) -> JsonResponse:
        json_resp = {
            "endpoint": self.endpoint,
            "reason": self.reason
        }
        response = JsonResponse(json_resp)
        if self.error_kind.id == ErrorKind.FORBIDDEN:
            response.status_code = HTTPStatus.FORBIDDEN
        if self.error_kind.id == ErrorKind.BAD_REQUEST:
            response.status_code = HTTPStatus.BAD_REQUEST
        if self.error_kind.id == ErrorKind.UNPROCESSABLE:
            response.status_code = HTTPStatus.UNPROCESSABLE_ENTITY

        return response
