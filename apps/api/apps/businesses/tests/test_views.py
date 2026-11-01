from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from apps.businesses.models import Business


User = get_user_model()


class BusinessListCreateViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create owner group
        self.owner_group = Group.objects.create(name="owner")

        # Create owner user
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="TestPassword123!",
        )
        self.owner.groups.add(self.owner_group)

        # Create normal user
        self.normal_user = User.objects.create_user(
            email="normal@example.com",
            password="TestPassword123!",
        )

        # Create another owner
        self.second_owner = User.objects.create_user(
            email="second@example.com",
            password="TestPassword123!",
        )
        self.second_owner.groups.add(self.owner_group)

        # Create businesses
        self.business = Business.objects.create(
            owner=self.owner,
            name="Bookito",
            slug="bookito",
            description="Appointment booking platform",
        )

        self.other_business = Business.objects.create(
            owner=self.second_owner,
            name="Other Business",
            slug="other-business",
        )

        self.url = reverse("businesses:business-list-create")

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    # -------------------------
    # GET Tests
    # -------------------------

    def test_owner_can_get_business_list(self):
        self.authenticate(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data["data"]), 1)

        self.assertEqual(
            response.data["data"][0]["slug"],
            "bookito",
        )

    def test_owner_can_only_see_own_businesses(self):
        self.authenticate(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        slugs = [
            business["slug"]
            for business in response.data["data"]
        ]

        self.assertIn("bookito", slugs)
        self.assertNotIn("other-business", slugs)

    # -------------------------
    # POST Tests
    # -------------------------

    def test_owner_can_create_business(self):
        self.authenticate(self.owner)

        payload = {
            "name": "New Business",
            "slug": "new-business",
            "description": "New business description",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Business.objects.filter(
                owner=self.owner,
                slug="new-business",
            ).exists()
        )

        business = Business.objects.get(slug="new-business")

        self.assertEqual(business.owner, self.owner)
        self.assertEqual(business.name, "New Business")
        self.assertEqual(business.status, Business.Status.DRAFT)

    def test_created_business_owner_is_current_user(self):
        self.authenticate(self.owner)

        payload = {
            "name": "New Business",
            "slug": "new-business",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        business = Business.objects.get(slug="new-business")

        self.assertEqual(business.owner_id, self.owner.id)

    def test_owner_cannot_create_business_with_duplicate_slug(self):
        self.authenticate(self.owner)

        payload = {
            "name": "Duplicate Business",
            "slug": "bookito",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

        self.assertEqual(
            Business.objects.filter(slug="bookito").count(),
            1,
        )

    def test_normal_user_cannot_access_business_list(self):
        self.authenticate(self.normal_user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_normal_user_cannot_create_business(self):
        self.authenticate(self.normal_user)

        payload = {
            "name": "Unauthorized Business",
            "slug": "unauthorized-business",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            Business.objects.filter(
                slug="unauthorized-business"
            ).exists()
        )

    def test_unauthenticated_user_cannot_access_business_list(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )