from django.shortcuts import get_object_or_404
from rest_framework import generics, status

from core.apiResponse.apiResponse import ApiResponse
from core.permissions.business import IsBusinessOwner

from ..models import Business
from ..serializers import (
    BusinessListSerializer,
    BusinessCreateSerializer,
    BusinessDetailSerializer,
    BusinessUpdateSerializer,
    SlugAvailabilitySerializer,
    SlugAvailabilityResultSerializer
)

from core.apiResponse.openapi import (
    envelope, ERR_400, ERR_401, ERR_403, ERR_404, ERR_409_SLUG,
)
from drf_spectacular.utils import extend_schema

ListEnvelope = envelope("BusinessListResponse", BusinessListSerializer, many=True)
DetailEnvelope = envelope("BusinessDetailResponse", BusinessDetailSerializer)
SlugEnvelope = envelope("SlugAvailabilityResponse", SlugAvailabilityResultSerializer)

TAG = ["Owner · Businesses"]


class BusinessListCreateView(generics.GenericAPIView):
    permission_classes = [IsBusinessOwner]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Business.objects.none()
        return Business.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BusinessCreateSerializer
        return BusinessListSerializer

    @extend_schema(
        operation_id="owner_businesses_list",
        tags=TAG,
        summary="List the owner's businesses",
        responses={200: ListEnvelope, 401: ERR_401, 403: ERR_403},
    )
    def get(self, request, *args, **kwargs):
        businesses = self.get_queryset()

        serializer = self.get_serializer(businesses, many=True)

        return ApiResponse.success(
            message="Businesses get successfully.",
            data=serializer.data,
        )

    @extend_schema(
        operation_id="owner_businesses_create",
        tags=TAG,
        summary="Create a business",
        request=BusinessCreateSerializer,
        responses={
            201: DetailEnvelope, 400: ERR_400, 401: ERR_401,
            403: ERR_403, 409: ERR_409_SLUG,
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        business = serializer.save(owner=request.user)

        response_serializer = BusinessDetailSerializer(business)

        return ApiResponse.success(
            message="Business created successfully.",
            data=response_serializer.data,
            status_code=status.HTTP_201_CREATED,
        )


class BusinessDetailView(generics.GenericAPIView):
    permission_classes = [IsBusinessOwner]

    lookup_field = "pk"
    lookup_url_kwarg = "business_id"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Business.objects.none()
        return Business.objects.filter(owner=self.request.user)

    def get_object(self):
        business = get_object_or_404(
            self.get_queryset(),
            **{self.lookup_field: self.kwargs[self.lookup_url_kwarg]},
        )
        self.check_object_permissions(self.request, business)
        return business

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return BusinessUpdateSerializer

        return BusinessDetailSerializer

    @extend_schema(
        operation_id="owner_businesses_retrieve",
        tags=TAG,
        summary="retrieve a business",
        responses={
            200: DetailEnvelope, 401: ERR_401,
            403: ERR_403, 404: ERR_404,
        },
    )
    def get(self, request, *args, **kwargs):
        business = self.get_object()

        serializer = self.get_serializer(business)

        return ApiResponse.success(
            message="Business retrieved successfully.",
            data=serializer.data,
        )

    @extend_schema(
        operation_id="owner_businesses_update",
        tags=TAG,
        summary="Update a business",
        request=BusinessUpdateSerializer,
        responses={
            200: DetailEnvelope, 400: ERR_400, 401: ERR_401,
            403: ERR_403, 404: ERR_404, 409: ERR_409_SLUG,
        },
    )
    def put(self, request, *args, **kwargs):
        business = self.get_object()

        serializer = self.get_serializer(
            business,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        business = serializer.save()

        response_serializer = BusinessDetailSerializer(business)

        return ApiResponse.success(
            message="Business updated successfully.",
            data=response_serializer.data,
        )


class SlugAvailabilityView(generics.GenericAPIView):
    permission_classes = [IsBusinessOwner]
    serializer_class = SlugAvailabilitySerializer

    @extend_schema(
        operation_id="owner_businesses_slug_availability",
        tags=TAG,
        summary="Check whether a slug is free",
        parameters=[SlugAvailabilitySerializer],
        responses={
            200: SlugEnvelope, 400: ERR_400, 401: ERR_401,
            403: ERR_403, 404: ERR_404,
        },
    )
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        slug = serializer.validated_data["slug"]
        business_id = serializer.validated_data.get("business_id")

        businesses = Business.objects.filter(slug=slug)

        if business_id is not None:
            # Only allow excluding a business owned by the current user.
            get_object_or_404(
                Business.objects.filter(owner=request.user),
                pk=business_id,
            )
            businesses = businesses.exclude(pk=business_id)

        available = not businesses.exists()

        message = (
            "Slug is available."
            if available
            else "Slug is already taken."
        )

        return ApiResponse.success(
            message=message,
            data={
                "slug": slug,
                "available": available,
            },
        )
