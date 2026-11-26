import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User


@pytest.mark.django_db
def test_profile_requires_authentication():
    assert APIClient().get(reverse("profile")).status_code == 401


@pytest.mark.django_db
def test_profile_returns_and_updates_normalized_full_name():
    user = User.objects.create_user(phone_number="09120000001")
    client = APIClient()
    client.force_authenticate(user)
    assert client.get(reverse("profile")).data["display_name"] == ""
    response = client.patch(
        reverse("profile"), {"display_name": "  علی   رضایی  "}, format="json"
    )
    assert response.status_code == 200
    assert response.data["display_name"] == "علی رضایی"
    user.refresh_from_db()
    assert user.display_name == "علی رضایی"


@pytest.mark.django_db
def test_profile_rejects_single_name():
    user = User.objects.create_user(phone_number="09120000002")
    client = APIClient()
    client.force_authenticate(user)
    response = client.patch(
        reverse("profile"), {"display_name": "علی"}, format="json"
    )
    assert response.status_code == 400
    user.refresh_from_db()
    assert user.display_name == ""
