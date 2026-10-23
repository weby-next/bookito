from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from ..serializers import (
    OTPRequestSerializer,
    OTPVerifySerializer,
    swaggerSerializer
)
from ..services import request_email_otp, verify_email_otp, blacklist_user_refresh_tokens
from drf_spectacular.utils import extend_schema, OpenApiResponse

User = get_user_model()


class OTPRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_request"

    @extend_schema(
        operation_id="request_email_otp",
        tags=["Authentication"],
        summary="Request email OTP",
        description=(
            "Requests a one-time verification code sent to the supplied email. "
            "A resend cooldown and rate limits apply."
        ),
        request=OTPRequestSerializer,
        auth=[],
        responses={
            200: swaggerSerializer.OTPRequestResponseSerializer,
            400: swaggerSerializer.ErrorResponseSerializer,
            403: swaggerSerializer.ErrorResponseSerializer,
            429: swaggerSerializer.ErrorResponseSerializer,
        },
    )

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            sent = request_email_otp(email)
        except Exception:
            # جزئیات خطا باید در لاگ سرور ثبت شود؛
            # اطلاعات حساس ایمیل یا OTP را لاگ نکن.
            return Response(
                {"detail": "ارسال کد در حال حاضر امکان‌پذیر نیست."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if not sent:
            return Response(
                {"detail": "لطفاً پیش از درخواست مجدد کمی صبر کنید."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        return Response(
            {
                "detail": "اگر درخواست قابل پردازش باشد، کد تأیید ارسال می‌شود.",
                "expires_in": 300,
            },
            status=status.HTTP_200_OK,
        )


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_verify"

    @extend_schema(
        operation_id="verify_email_otp",
        tags=["Authentication"],
        summary="Verify email OTP and obtain tokens",
        description=(
            "Verifies the one-time code sent to an email address. "
            "On successful verification, returns access and refresh tokens."
        ),
        request=OTPVerifySerializer,
        auth=[],
        responses={
            200: swaggerSerializer.OTPVerifyResponseSerializer,
            400: swaggerSerializer.ErrorResponseSerializer,
            403: swaggerSerializer.ErrorResponseSerializer,
            429: swaggerSerializer.ErrorResponseSerializer,
        },
    )

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        if not verify_email_otp(email, code):
            return Response(
                {"detail": "کد تأیید نامعتبر است یا اعتبار آن پایان یافته است."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ورود کاربران موجود یا ثبت‌نام اولیه کاربران جدید
        user, created = User.objects.get_or_create(email=email)

        if not user.is_active:
            return Response(
                {"detail": "این حساب کاربری غیرفعال است."},
                status=status.HTTP_403_FORBIDDEN,
            )
        blacklist_user_refresh_tokens(user)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": str(user.pk),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                "created": created,
            },
            status=status.HTTP_200_OK,
        )