from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.sms import SMSDeliveryNotConfigured


@pytest.mark.django_db
def test_otp_request_route_is_mounted_and_does_not_leak_code_without_sms_provider():
    with patch("apps.accounts.views.send_login_code", side_effect=SMSDeliveryNotConfigured):
        response = APIClient().post(
            reverse("request-otp"),
            {"phone_number": "09121110009"},
            format="json",
        )

    assert response.status_code == 503
    assert "code" not in response.data
    assert response.data["detail"] == "ارسال پیامک هنوز پیکربندی نشده است."
