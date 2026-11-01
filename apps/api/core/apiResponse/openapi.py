from django.db import models
from drf_spectacular.utils import OpenApiResponse
from rest_framework import serializers


class ErrorCode(models.TextChoices):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    OTP_INVALID = "OTP_INVALID"
    OTP_EXPIRED = "OTP_EXPIRED"
    UNAUTHENTICATED = "UNAUTHENTICATED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    SLUG_TAKEN = "SLUG_TAKEN"
    PUBLISH_INCOMPLETE = "PUBLISH_INCOMPLETE"
    OTP_RATE_LIMITED = "OTP_RATE_LIMITED"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


class ErrorResponseSerializer(serializers.Serializer):
    code = serializers.ChoiceField(choices=ErrorCode.choices)
    message = serializers.CharField()
    # فقط برای خطای فیلدها
    fields = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()),
        required=False,
    )


_envelopes = {}

def envelope(name, data_serializer, many=False):
    """شکل واقعی ApiResponse.success را مستند می‌کند: {success, message, data}."""
    if name not in _envelopes:
        _envelopes[name] = type(name, (serializers.Serializer,), {
            "success": serializers.BooleanField(),
            "message": serializers.CharField(),
            "data": data_serializer(many=many),
        })
    return _envelopes[name]


def error(description):
    return OpenApiResponse(response=ErrorResponseSerializer, description=description)

ERR_400 = error("VALIDATION_ERROR")
ERR_401 = error("UNAUTHENTICATED")
ERR_403 = error("FORBIDDEN")
ERR_404 = error("NOT_FOUND")
ERR_409_SLUG = error("SLUG_TAKEN")