from __future__ import annotations
from http import HTTPStatus

from django.http import JsonResponse

class ErrorKind:
    _FORBIDDEN = 0
    _BAD_REQUEST = 1
    _UNPROCESSABLE = 2

    def __init__(self, id: int) -> None:
        self.id = id

    def forbidden() -> ErrorKind:
        return ErrorKind(ErrorKind._FORBIDDEN)

    def bad_request() -> ErrorKind:
        return ErrorKind(ErrorKind._BAD_REQUEST)

    def unprocessable() -> ErrorKind:
        return ErrorKind(ErrorKind._UNPROCESSABLE)

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
        if self.error_kind.id == ErrorKind._FORBIDDEN:
            response.status_code = HTTPStatus.FORBIDDEN
        if self.error_kind.id == ErrorKind._BAD_REQUEST:
            response.status_code = HTTPStatus.BAD_REQUEST
        if self.error_kind.id == ErrorKind._UNPROCESSABLE:
            response.status_code = HTTPStatus.UNPROCESSABLE_ENTITY

        return response
