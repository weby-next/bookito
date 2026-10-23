from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class OTPRequestResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    expires_in = serializers.IntegerField()


class AuthenticatedUserSerializer(serializers.Serializer):
    id = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField(
        allow_null=True,
        required=False,
    )
    last_name = serializers.CharField(
        allow_null=True,
        required=False,
    )


class OTPVerifyResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = AuthenticatedUserSerializer()
    created = serializers.BooleanField()


class SessionResponseSerializer(serializers.Serializer):
    authenticated = serializers.BooleanField()
    user = AuthenticatedUserSerializer()


class RefreshTokenRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class RefreshTokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()