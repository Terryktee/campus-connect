from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import serializers
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.viewsets import GenericViewSet

from core.mixins import InstitutionScopedQuerysetMixin
from core.models import Admin, Category, Channel, Institution


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ("id", "name")


class InstitutionScopedView(InstitutionScopedQuerysetMixin, GenericViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer


class AdminAuthTests(APITestCase):
    def setUp(self):
        self.institution = Institution.objects.create(
            name="University One", short_code="U1", city="Harare"
        )
        self.other_institution = Institution.objects.create(
            name="University Two", short_code="U2", city="Bulawayo"
        )
        category = Category.objects.create(name="News", slug="news")
        Channel.objects.create(
            slug="one-news",
            name="One News",
            category_focus=category,
            institution=self.institution,
            claim_contact="one@example.com",
        )
        Channel.objects.create(
            slug="two-news",
            name="Two News",
            category_focus=category,
            institution=self.other_institution,
            claim_contact="two@example.com",
        )
        self.moderator = get_user_model().objects.create_user(
            username="moderator", password="secret123"
        )
        Admin.objects.create(
            user=self.moderator,
            role=Admin.Role.MODERATOR,
            institution=self.institution,
        )
        self.super_admin = get_user_model().objects.create_user(
            username="superadmin", password="secret123", first_name="Super"
        )
        Admin.objects.create(user=self.super_admin, role=Admin.Role.SUPER_ADMIN)

    def test_admin_endpoint_requires_jwt(self):
        response = self.client.get(reverse("admin-me"))
        self.assertEqual(response.status_code, 401)

    def test_me_returns_admin_profile(self):
        response = self.client.post(
            reverse("auth-login"),
            {"username": "moderator", "password": "secret123"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        response = self.client.get(reverse("admin-me"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {"name": "moderator", "role": "moderator", "institution": "University One"},
        )

    def test_moderator_queryset_is_scoped_to_institution(self):
        request = APIRequestFactory().get("/")
        request.admin_profile = self.moderator.admin
        view = InstitutionScopedView()
        view.request = request
        institutions = view.get_queryset()
        self.assertEqual(institutions.count(), 1)
        self.assertEqual(institutions.get().institution_id, self.institution.pk)

    def test_super_admin_queryset_is_not_scoped(self):
        request = APIRequestFactory().get("/")
        request.admin_profile = self.super_admin.admin
        view = InstitutionScopedView()
        view.request = request
        self.assertEqual(view.get_queryset().count(), 2)

    def test_invite_requires_super_admin(self):
        login = self.client.post(
            reverse("auth-login"),
            {"username": "moderator", "password": "secret123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        response = self.client.post(
            reverse("admin-invite"),
            {
                "username": "newmoderator",
                "email": "new@example.com",
                "role": "moderator",
                "institution": self.institution.pk,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_super_admin_can_invite_user_with_unusable_password(self):
        login = self.client.post(
            reverse("auth-login"),
            {"username": "superadmin", "password": "secret123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        response = self.client.post(
            reverse("admin-invite"),
            {
                "username": "newmoderator",
                "email": "new@example.com",
                "role": "moderator",
                "institution": self.institution.pk,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        invited = get_user_model().objects.get(username="newmoderator")
        self.assertFalse(invited.has_usable_password())
        self.assertEqual(invited.admin.role, Admin.Role.MODERATOR)
