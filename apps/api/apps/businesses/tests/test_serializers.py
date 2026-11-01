from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.businesses.models import Business
from apps.businesses.serializers import (
    BusinessCreateSerializer,
    BusinessUpdateSerializer,
    BusinessListSerializer,
    BusinessDetailSerializer,
    SlugAvailabilitySerializer,
    SlugTakenError
)


User = get_user_model()


class BusinessSerializerTest(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="TestPassword123!",
        )

        self.business = Business.objects.create(
            owner=self.owner,
            name="Bookito",
            slug="bookito",
            description="Appointment booking platform",
        )

    # -------------------------
    # Create Serializer
    # -------------------------

    def test_create_serializer_valid_data(self):
        data = {
            "name": "New Business",
            "slug": "new-business",
            "description": "Test description",
        }

        serializer = BusinessCreateSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_create_serializer_normalizes_slug(self):
        data = {
            "name": "New Business",
            "slug": "NEW-BUSINESS",
        }

        serializer = BusinessCreateSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        self.assertEqual(
            serializer.validated_data["slug"],
            "new-business",
        )

    def test_create_serializer_rejects_empty_name(self):
        data = {
            "name": "",
            "slug": "new-business",
        }

        serializer = BusinessCreateSerializer(data=data)

        self.assertFalse(serializer.is_valid())

        self.assertIn("name", serializer.errors)

    def test_create_serializer_rejects_duplicate_slug(self):
        data = {
            "name": "Another Business",
            "slug": "bookito",
        }

        serializer = BusinessCreateSerializer(data=data)

        with self.assertRaises(SlugTakenError):
            serializer.is_valid()

    # -------------------------
    # Update Serializer
    # -------------------------

    def test_update_serializer_valid_data(self):
        data = {
            "name": "Updated Bookito",
        }

        serializer = BusinessUpdateSerializer(
            instance=self.business,
            data=data,
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_update_serializer_allows_current_slug(self):
        data = {
            "slug": "bookito",
        }

        serializer = BusinessUpdateSerializer(
            instance=self.business,
            data=data,
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_update_serializer_normalizes_slug(self):
        data = {
            "slug": "BOOKITO",
        }

        serializer = BusinessUpdateSerializer(
            instance=self.business,
            data=data,
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        self.assertEqual(
            serializer.validated_data["slug"],
            "bookito",
        )

    # -------------------------
    # Slug Availability Serializer
    # -------------------------

    def test_slug_availability_valid_data(self):
        data = {
            "slug": "new-business",
        }

        serializer = SlugAvailabilitySerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_slug_availability_normalizes_slug(self):
        data = {
            "slug": "NEW-BUSINESS",
        }

        serializer = SlugAvailabilitySerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        self.assertEqual(
            serializer.validated_data["slug"],
            "new-business",
        )

    def test_slug_availability_rejects_invalid_business_id(self):
        data = {
            "slug": "new-business",
            "business_id": -1,
        }

        serializer = SlugAvailabilitySerializer(data=data)

        self.assertFalse(serializer.is_valid())

        self.assertIn("business_id", serializer.errors)

    def test_slug_availability_rejects_zero_business_id(self):
        data = {
            "slug": "new-business",
            "business_id": 0,
        }

        serializer = SlugAvailabilitySerializer(data=data)

        self.assertFalse(serializer.is_valid())

        self.assertIn("business_id", serializer.errors)

    # -------------------------
    # Read-only Serializers
    # -------------------------

    def test_business_list_serializer_fields_are_read_only(self):
        serializer = BusinessListSerializer(instance=self.business)

        self.assertIn("id", serializer.data)
        self.assertEqual(serializer.data["name"], "Bookito")

        self.assertEqual(
            set(serializer.fields.keys()),
            {"id", "name", "slug", "status", "created_at"},
        )

        for field in serializer.fields.values():
            self.assertTrue(field.read_only)

    def test_business_detail_serializer_fields_are_read_only(self):
        serializer = BusinessDetailSerializer(instance=self.business)

        self.assertEqual(serializer.data["name"], "Bookito")

        for field in serializer.fields.values():
            self.assertTrue(field.read_only)