from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    OTPRequestView,
    OTPVerifyView,
    SessionView,
    LogoutView,
    BookitoTokenRefreshView
)

app_name = "authentication"

urlpatterns = [
    path("refresh-token", BookitoTokenRefreshView.as_view(), name="refresh-token"),

    path("otp/request", OTPRequestView.as_view(), name="otp-request"),
    path("otp/verify", OTPVerifyView.as_view(), name="otp-verify"),
    path("session", SessionView.as_view(), name="session"),
    path("logout", LogoutView.as_view(), name="logout"),
]
