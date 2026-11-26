import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User


@pytest.mark.django_db
def test_profile_requires_authentication():
    response = APIClient().get(reverse("profile"))
    assert response.status_code == 401


@pytest.mark.django_db
def test_profile_returns_and_updates_full_display_name():
    user = User.objects.create_user(phone_number="09120000001")
    client = APIClient()
    client.force_authenticate(user)

    initial = client.get(reverse("profile"))
    assert initial.status_code == 200
    assert initial.data["display_name"] == ""

    updated = client.patch(
        reverse("profile"),
        {"display_name": "  علی   رضایی  "},
        format="json",
    )
    assert updated.status_code == 200
    assert updated.data["display_name"] == "علی رضایی"

    user.refresh_from_db()
    assert user.display_name == "علی رضایی"


@pytest.mark.django_db
def test_profile_rejects_single_name_without_family_name():
    user = User.objects.create_user(phone_number="09120000002")
    client = APIClient()
    client.force_authenticate(user)

    response = client.patch(
        reverse("profile"),
        {"display_name": "علی"},
        format="json",
    )

    assert response.status_code == 400
    user.refresh_from_db()
    assert user.display_name == ""
