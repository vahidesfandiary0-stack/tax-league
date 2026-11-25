from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import OTPChallenge, User
from apps.accounts.sms import SMSDeliveryFailed, SMSDeliveryNotConfigured


@pytest.mark.django_db
def test_otp_request_route_is_mounted_and_does_not_leak_code_without_sms_provider():
    with patch("apps.accounts.views.send_login_code", side_effect=SMSDeliveryNotConfigured):
        response = APIClient().post(
            reverse("request-otp"),
            {"phone_number": "09121110009"},
            format="json",
            secure=True,
        )

    assert response.status_code == 503
    assert "code" not in response.data
    assert response.data["detail"] == "ارسال پیامک هنوز پیکربندی نشده است."
    assert OTPChallenge.objects.filter(
        phone_number="09121110009", consumed_at__isnull=False
    ).exists()


@pytest.mark.django_db
def test_otp_request_consumes_challenge_after_provider_failure():
    with patch("apps.accounts.views.send_login_code", side_effect=SMSDeliveryFailed):
        response = APIClient().post(
            reverse("request-otp"),
            {"phone_number": "09121110008"},
            format="json",
            secure=True,
        )

    assert response.status_code == 503
    assert "code" not in response.data
    assert response.data["detail"] == "ارسال پیامک در حال حاضر ممکن نیست؛ دوباره تلاش کنید."
    assert OTPChallenge.objects.filter(
        phone_number="09121110008", consumed_at__isnull=False
    ).exists()



@pytest.mark.django_db
def test_verify_otp_saves_selected_province_without_auto_verifying_it():
    with patch("apps.accounts.views.verify_challenge", return_value=True):
        response = APIClient().post(
            reverse("verify-otp"),
            {
                "phone_number": "09121110007",
                "code": "123456",
                "province": "خوزستان",
            },
            format="json",
            secure=True,
        )

    assert response.status_code == 200
    user = User.objects.get(phone_number="09121110007")
    assert user.province == "خوزستان"
    assert user.province_verified is False
    assert response.data["user"]["province"] == "خوزستان"
    assert response.data["user"]["province_verified"] is False
