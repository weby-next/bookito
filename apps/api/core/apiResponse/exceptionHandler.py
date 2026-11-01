import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler, set_rollback

from core.apiResponse.openapi import ErrorCode

logger = logging.getLogger(__name__)

VALID_CODES = set(ErrorCode.values)
OTP_THROTTLE_SCOPES = {"otp_request", "otp_verify"}


def _normalize_fields(data):
    """fields باید همیشه dict باشد: {field_name: [messages]}."""
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        return {"non_field_errors": data}
    return {"non_field_errors": [str(data)]}


def _code_for_api_exception(exc, status_code):
    raw = exc.get_codes()
    # اگر exception خودش code معتبر دارد (مثل SLUG_TAKEN یا OTP_INVALID)
    if isinstance(raw, str) and raw in VALID_CODES:
        return raw
    # ParseError و دیگر خطاهای ۴xx که خطای درخواست کلاینت‌اند
    if status_code < 500:
        return ErrorCode.VALIDATION_ERROR
    return ErrorCode.INTERNAL_ERROR


def custom_exception_handler(exc, context):
    # ۱) خطاهای Django را قبل از isinstance به معادل DRF تبدیل می‌کنیم
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = exceptions.PermissionDenied()

    response = exception_handler(exc, context)

    # ۲) خطای پیش‌بینی‌نشده: لاگ و پاسخ JSON با ۵۰۰
    if response is None:
        logger.error("Unhandled exception", exc_info=exc)
        set_rollback()
        return Response(
            {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "An unexpected error occurred.",
            },
            status=500,
        )

    code = ErrorCode.INTERNAL_ERROR
    message = "An unexpected error occurred."
    fields = None

    if isinstance(exc, exceptions.ValidationError):
        code = ErrorCode.VALIDATION_ERROR
        message = "Invalid request data."
        fields = _normalize_fields(response.data)

    elif isinstance(exc, exceptions.NotAuthenticated):
        code = ErrorCode.UNAUTHENTICATED
        message = "Authentication credentials were not provided."

    elif isinstance(exc, exceptions.AuthenticationFailed):
        code = ErrorCode.UNAUTHENTICATED
        message = "Authentication credentials are invalid."

    elif isinstance(exc, exceptions.PermissionDenied):
        code = ErrorCode.FORBIDDEN
        message = "You do not have permission to perform this action."

    elif isinstance(exc, exceptions.NotFound):
        code = ErrorCode.NOT_FOUND
        message = "The requested resource was not found."

    elif isinstance(exc, exceptions.Throttled):
        scope = getattr(context.get("view"), "throttle_scope", None)
        code = (
            ErrorCode.OTP_RATE_LIMITED
            if scope in OTP_THROTTLE_SCOPES
            else ErrorCode.RATE_LIMITED
        )
        message = "Too many requests. Please try again later."

    elif isinstance(exc, exceptions.APIException):
        code = _code_for_api_exception(exc, response.status_code)
        message = str(exc.detail)

    body = {"code": str(code), "message": message}
    if fields is not None:
        body["fields"] = fields

    response.data = body
    return response