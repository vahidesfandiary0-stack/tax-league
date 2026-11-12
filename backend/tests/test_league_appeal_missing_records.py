from uuid import uuid4

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_filing_appeal_for_missing_attempt_returns_bad_request():
    user = get_user_model().objects.create_user(phone_number="09120000091")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/league/appeals/",
        {
            "attempt_id": str(uuid4()),
            "reason": "اشکال در نتیجه",
            "details": "لطفاً نتیجه بررسی شود.",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_reviewing_missing_appeal_returns_bad_request():
    manager = get_user_model().objects.create_superuser(
        phone_number="09120000092", password="test-password"
    )
    client = APIClient()
    client.force_authenticate(user=manager)

    response = client.post(
        f"/api/v1/league/appeals/{uuid4()}/review/",
        {"decision": "rejected", "decision_note": "رکوردی برای بررسی وجود ندارد."},
        format="json",
    )

    assert response.status_code == 400
