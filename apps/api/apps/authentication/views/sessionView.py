from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from ..serializers import (
    LogoutSerializer,
    swaggerSerializer
)
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework_simplejwt.views import TokenRefreshView


class SessionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="get_current_session",
        tags=["Authentication"],
        summary="Get current authenticated user",
        description="Returns the identity information of the current user.",
        responses={
            200: swaggerSerializer.SessionResponseSerializer,
            401: swaggerSerializer.ErrorResponseSerializer,
        },
    )

    def get(self, request):
        user = request.user

        return Response(
            {
                "authenticated": True,
                "user": {
                    "id": str(user.pk),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="logout",
        tags=["Authentication"],
        summary="Logout and revoke refresh token",
        description=(
            "Revokes the supplied refresh token by adding it to the blacklist."
        ),
        request=LogoutSerializer,
        auth=[],
        responses={
            204: OpenApiResponse(
                description="Refresh token revoked successfully."
            ),
            400: swaggerSerializer.ErrorResponseSerializer,
            401: swaggerSerializer.ErrorResponseSerializer,
        },
    )

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh = RefreshToken(
                serializer.validated_data["refresh"]
            )
            refresh.blacklist()
        except TokenError:
            return Response(
                {"detail": "Refresh Token نامعتبر یا باطل شده است."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class BookitoTokenRefreshView(TokenRefreshView):

    @extend_schema(
        operation_id="refresh_access_token",
        tags=["Authentication"],
        summary="Refresh authentication tokens",
        description=(
            "Accepts a valid refresh token and returns a new access token. "
            "With refresh token rotation enabled, a new refresh token "
            "is returned and the previous token is blacklisted."
        ),
        request=swaggerSerializer.RefreshTokenRequestSerializer,
        auth=[],
        responses={
            200: swaggerSerializer.RefreshTokenResponseSerializer,
            401: swaggerSerializer.ErrorResponseSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)