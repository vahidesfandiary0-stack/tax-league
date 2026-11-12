import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen


class SMSDeliveryError(Exception):
    """Base class for safe-to-report SMS delivery failures."""


class SMSDeliveryNotConfigured(SMSDeliveryError):
    pass


class SMSDeliveryFailed(SMSDeliveryError):
    pass


def send_login_code(phone_number, code):
    """
    Send a one-time login code through Kavenegar VerifyLookup.

    Required environment:
      SMS_PROVIDER=kavenegar
      KAVENEGAR_API_KEY=<secret>
      KAVENEGAR_OTP_TEMPLATE=<approved template name>

    The template must contain the provider's expected token placeholder.
    Secrets must only be configured in the server secret manager.
    """
    provider = os.getenv("SMS_PROVIDER", "").strip().lower()
    if provider != "kavenegar":
        raise SMSDeliveryNotConfigured("SMS provider is not configured")

    api_key = os.getenv("KAVENEGAR_API_KEY", "").strip()
    template = os.getenv("KAVENEGAR_OTP_TEMPLATE", "").strip()
    if not api_key or not template:
        raise SMSDeliveryNotConfigured("Kavenegar credentials or template are missing")

    url = (
        "https://api.kavenegar.com/v1/"
        f"{quote(api_key, safe='')}/verify/lookup.json"
    )
    payload = urlencode({
        "receptor": phone_number,
        "token": code,
        "template": template,
    }).encode("utf-8")
    request = Request(
        url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, ValueError):
        # Never include provider response, API key, phone number, or OTP in the
        # exception text returned to the API client or application logs.
        raise SMSDeliveryFailed("SMS provider request failed") from None

    provider_status = result.get("return", {}).get("status")
    if provider_status != 200:
        raise SMSDeliveryFailed("SMS provider rejected the request")

    return result
