from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Admin, Institution, OrientationGuide


class OrientationApiTests(APITestCase):
    def setUp(self):
        self.institution = Institution.objects.create(
            name="One", short_code="ONE", city="Harare"
        )
        self.other_institution = Institution.objects.create(
            name="Two", short_code="TWO", city="Bulawayo"
        )
        self.published = OrientationGuide.objects.create(
            institution=self.institution,
            guide_type=OrientationGuide.GuideType.HOW_TO,
            title="Register",
            content="Register online.",
            sort_order=2,
            is_published=True,
        )
        self.other_published = OrientationGuide.objects.create(
            institution=self.institution,
            guide_type=OrientationGuide.GuideType.DIRECTORY_ENTRY,
            title="Registry",
            content="Visit registry.",
            sort_order=1,
            is_published=True,
        )
        OrientationGuide.objects.create(
            institution=self.institution,
            guide_type=OrientationGuide.GuideType.HOW_TO,
            title="Draft",
            content="Not public.",
            is_published=False,
        )
        user = get_user_model().objects.create_user(
            username="moderator", password="secret123"
        )
        Admin.objects.create(
            user=user, role=Admin.Role.MODERATOR, institution=self.institution
        )
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_public_guides_are_active_published_grouped_and_ordered(self):
        response = self.client.get(
            reverse("orientation-guide-list", args=("ONE",))
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.data["how_to"]], [self.published.pk])
        self.assertEqual(
            [item["id"] for item in response.data["directory_entry"]],
            [self.other_published.pk],
        )
        self.assertEqual(response.data["campus_map_note"], [])

        self.published.is_published = False
        self.published.save(update_fields=("is_published",))
        response = self.client.get(
            reverse("orientation-guide-list", args=("ONE",))
        )
        self.assertEqual(response.data["how_to"], [])

    def test_inactive_or_unknown_institution_is_not_public(self):
        self.institution.is_active = False
        self.institution.save(update_fields=("is_active",))
        self.assertEqual(
            self.client.get(reverse("orientation-guide-list", args=("ONE",))).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse("orientation-guide-list", args=("MISSING",))).status_code,
            404,
        )

    def test_moderator_can_crud_own_guides_but_not_foreign_guides(self):
        own = self.client.post(
            reverse("admin-orientation-list"),
            {
                "institution": self.institution.pk,
                "guide_type": "campus_map_note",
                "title": "Map",
                "content": "Main gate.",
                "is_published": True,
            },
            format="json",
        )
        self.assertEqual(own.status_code, 201)
        own_id = own.data["id"]

        foreign_create = self.client.post(
            reverse("admin-orientation-list"),
            {
                "institution": self.other_institution.pk,
                "guide_type": "how_to",
                "title": "Foreign",
                "content": "No access.",
            },
            format="json",
        )
        self.assertEqual(foreign_create.status_code, 403)

        foreign = OrientationGuide.objects.create(
            institution=self.other_institution,
            guide_type="how_to",
            title="Foreign",
            content="No access.",
        )
        response = self.client.patch(
            reverse("admin-orientation-detail", args=(foreign.pk,)),
            {"title": "Changed"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)
        foreign.refresh_from_db()
        self.assertEqual(foreign.title, "Foreign")

        response = self.client.delete(
            reverse("admin-orientation-detail", args=(own_id,))
        )
        self.assertEqual(response.status_code, 204)
