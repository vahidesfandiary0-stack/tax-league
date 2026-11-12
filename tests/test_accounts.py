import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.accounts.models import OTPChallenge
from apps.accounts.otp import issue_challenge, verify_challenge


@pytest.mark.django_db
def test_otp_challenge_is_single_use():
    phone = "+989121234567"
    challenge, code = issue_challenge(phone)
    assert verify_challenge(phone, code) is True
    assert verify_challenge(phone, code) is False
    challenge.refresh_from_db()
    assert challenge.consumed_at is not None


@pytest.mark.django_db
def test_otp_rejects_wrong_code_and_counts_attempt():
    phone = "+989121234568"
    challenge, code = issue_challenge(phone)
    assert verify_challenge(phone, "000000" if code != "000000" else "000001") is False
    challenge.refresh_from_db()
    assert challenge.attempts == 1
    assert challenge.consumed_at is None


@pytest.mark.django_db
def test_request_otp_reports_provider_not_configured_without_leaking_code():
    response = APIClient().post(
        "/api/v1/auth/request-otp/",
        {"phone_number": "+989121234569"},
        format="json",
    )
    assert response.status_code == 503
    assert "code" not in response.data
    challenge = OTPChallenge.objects.get(phone_number="+989121234569")
    assert challenge.consumed_at is not None


@pytest.mark.django_db
def test_verify_otp_creates_user_and_token():
    phone = "+989121234570"
    challenge, code = issue_challenge(phone)
    response = APIClient().post(
        "/api/v1/auth/verify-otp/",
        {"phone_number": phone, "code": code},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["token"]
    assert get_user_model().objects.filter(phone_number=phone).exists()
