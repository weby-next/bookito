from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIRequestFactory

from apps.businesses.models import Business
from core.permissions.business import IsBusinessOwner


User = get_user_model()


class IsBusinessOwnerPermissionTest(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsBusinessOwner()

        # Create owner group
        self.owner_group = Group.objects.create(name="owner")

        # Create first user
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="TestPassword123!",
        )

        self.owner.groups.add(self.owner_group)

        # Create second user without owner role
        self.normal_user = User.objects.create_user(
            email="normal@example.com",
            password="TestPassword123!",
        )

        # Create business for owner
        self.business = Business.objects.create(
            owner=self.owner,
            name="Bookito",
            slug="bookito",
        )

    def test_owner_group_has_permission(self):
        request = self.factory.get("/")
        request.user = self.owner

        self.assertTrue(
            self.permission.has_permission(request, None)
        )

    def test_normal_user_does_not_have_permission(self):
        request = self.factory.get("/")
        request.user = self.normal_user

        self.assertFalse(
            self.permission.has_permission(request, None)
        )

    def test_owner_can_access_own_business(self):
        request = self.factory.get("/")
        request.user = self.owner

        self.assertTrue(
            self.permission.has_object_permission(
                request,
                None,
                self.business,
            )
        )

    def test_owner_cannot_access_another_users_business(self):
        request = self.factory.get("/")
        request.user = self.normal_user

        self.assertFalse(
            self.permission.has_object_permission(
                request,
                None,
                self.business,
            )
        )

    def test_unauthenticated_user_does_not_have_permission(self):
        request = self.factory.get("/")
        request.user = None

        self.assertFalse(
            self.permission.has_permission(request, None)
        )