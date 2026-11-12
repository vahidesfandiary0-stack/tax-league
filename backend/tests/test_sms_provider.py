import json
from io import BytesIO
from unittest.mock import patch

import pytest

from apps.accounts.sms import (
    SMSDeliveryFailed,
    SMSDeliveryNotConfigured,
    send_login_code,
)


def test_sms_provider_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("SMS_PROVIDER", raising=False)
    with pytest.raises(SMSDeliveryNotConfigured):
        send_login_code("09121110009", "123456")


def test_kavenegar_verify_lookup_uses_template_and_does_not_return_otp_in_url(monkeypatch):
    monkeypatch.setenv("SMS_PROVIDER", "kavenegar")
    monkeypatch.setenv("KAVENEGAR_API_KEY", "test-secret")
    monkeypatch.setenv("KAVENEGAR_OTP_TEMPLATE", "tax_league_login")
    response = BytesIO(json.dumps({"return": {"status": 200}}).encode())
    response.__enter__ = lambda self: self
    response.__exit__ = lambda *args: None

    with patch("apps.accounts.sms.urlopen", return_value=response) as mocked:
        result = send_login_code("09121110009", "123456")

    request = mocked.call_args.args[0]
    assert request.full_url.endswith("/verify/lookup.json")
    assert "123456" not in request.full_url
    assert b"token=123456" in request.data
    assert b"template=tax_league_login" in request.data
    assert result["return"]["status"] == 200


def test_kavenegar_provider_error_is_safely_wrapped(monkeypatch):
    monkeypatch.setenv("SMS_PROVIDER", "kavenegar")
    monkeypatch.setenv("KAVENEGAR_API_KEY", "test-secret")
    monkeypatch.setenv("KAVENEGAR_OTP_TEMPLATE", "tax_league_login")
    response = BytesIO(json.dumps({"return": {"status": 401}}).encode())
    response.__enter__ = lambda self: self
    response.__exit__ = lambda *args: None

    with patch("apps.accounts.sms.urlopen", return_value=response):
        with pytest.raises(SMSDeliveryFailed):
            send_login_code("09121110009", "123456")
