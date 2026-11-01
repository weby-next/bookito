from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

from apps.businesses.models import Business


User = get_user_model()


class BusinessModelTest(TestCase):

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

    def test_business_creation(self):
        """Business should be created successfully."""

        self.assertEqual(self.business.name, "Bookito")
        self.assertEqual(self.business.slug, "bookito")
        self.assertEqual(self.business.owner, self.owner)

    def test_default_status_is_draft(self):
        """New business should have draft status."""

        self.assertEqual(
            self.business.status,
            Business.Status.DRAFT,
        )

    def test_business_str_returns_name(self):
        """String representation should return business name."""

        self.assertEqual(str(self.business), "Bookito")

    def test_owner_can_have_multiple_businesses(self):
        """One owner should be able to create multiple businesses."""

        second_business = Business.objects.create(
            owner=self.owner,
            name="Bookito Academy",
            slug="bookito-academy",
        )

        self.assertEqual(self.owner.businesses.count(), 2)

        self.assertIn(
            second_business,
            self.owner.businesses.all(),
        )

    def test_slug_must_be_unique(self):
        """Duplicate slug should not be allowed."""

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Business.objects.create(
                    owner=self.owner,
                    name="Another Business",
                    slug="bookito",
                )

    def test_deleting_owner_is_protected(self):
        """Owner should not be deleted while businesses exist."""

        with self.assertRaises(ProtectedError):
            self.owner.delete()