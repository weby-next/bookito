from django.urls import path

from .views import (
    SlugAvailabilityView,
    BusinessListCreateView,
    BusinessDetailView
)

app_name = "businesses"

urlpatterns = [
    path(
        "owner/businesses/",
        BusinessListCreateView.as_view(),
        name="business-list-create",
    ),
    path(
        "owner/businesses/slug-availability/",
        SlugAvailabilityView.as_view(),
        name="business-slug-availability",
    ),
    path(
        "owner/businesses/<int:business_id>/",
        BusinessDetailView.as_view(),
        name="business-detail",
    ),
]