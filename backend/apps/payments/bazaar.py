import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


class BazaarConfigurationError(Exception):
    pass


class BazaarVerificationError(Exception):
    pass


def _request_json(url, data=None):
    headers = {"Accept": "application/json"}
    body = None
    if data is not None:
        body = urlencode(data).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    try:
        with urlopen(Request(url, data=body, headers=headers), timeout=12) as response:
            return json.loads(response.read(131072).decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read(2048).decode("utf-8", errors="replace")
        raise BazaarVerificationError(f"Bazaar API HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError, ValueError) as exc:
        raise BazaarVerificationError("ارتباط امن با سرویس تأیید کافه‌بازار برقرار نشد.") from exc


def _config():
    names = ("BAZAAR_CLIENT_ID", "BAZAAR_CLIENT_SECRET", "BAZAAR_REFRESH_TOKEN", "BAZAAR_PACKAGE_NAME")
    values = {name: getattr(settings, name, "") for name in names}
    if any(not value for value in values.values()):
        raise BazaarConfigurationError("تنظیمات اتصال توسعه‌دهنده کافه‌بازار روی سرور کامل نیست.")
    return values


def _access_token(config):
    cached = cache.get("raqtiva_bazaar_access_token")
    if cached:
        return cached
    result = _request_json(
        "https://pardakht.cafebazaar.ir/devapi/v2/auth/token/",
        {"grant_type": "refresh_token", "client_id": config["BAZAAR_CLIENT_ID"],
         "client_secret": config["BAZAAR_CLIENT_SECRET"], "refresh_token": config["BAZAAR_REFRESH_TOKEN"]},
    )
    if not isinstance(result, dict):
        raise BazaarVerificationError("پاسخ دریافت توکن کافه‌بازار ساختار معتبر ندارد.")
    token = result.get("access_token")
    if not isinstance(token, str) or not token:
        raise BazaarVerificationError("کافه‌بازار توکن دسترسی معتبر برنگرداند.")
    try:
        expires_in = int(result.get("expires_in", 3600))
    except (TypeError, ValueError) as exc:
        raise BazaarVerificationError("مدت اعتبار توکن کافه‌بازار معتبر نیست.") from exc
    if expires_in <= 0:
        raise BazaarVerificationError("مدت اعتبار توکن کافه‌بازار معتبر نیست.")
    cache.set("raqtiva_bazaar_access_token", token, timeout=max(1, expires_in - 60))
    return token


def ensure_bazaar_ready():
    config = _config()
    _access_token(config)


def verify_bazaar_subscription(product_id, purchase_token):
    config = _config()
    access_token = _access_token(config)
    url = (
        "https://pardakht.cafebazaar.ir/devapi/v2/api/applications/"
        f"{quote(config['BAZAAR_PACKAGE_NAME'], safe='')}/subscriptions/{quote(product_id, safe='')}"
        f"/purchases/{quote(purchase_token, safe='')}/?{urlencode({'access_token': access_token})}"
    )
    result = _request_json(url)
    if not isinstance(result, dict):
        raise BazaarVerificationError("پاسخ تأیید کافه‌بازار ساختار معتبر ندارد.")
    if result.get("error") or result.get("error_description"):
        detail = str(result.get("error_description") or result.get("error"))[:300]
        raise BazaarVerificationError(f"کافه‌بازار خرید را تأیید نکرد: {detail}")
    try:
        # CafeBazaar Developer API v2 returns validUntilTimestampMsec;
        # expiryTimeMillis/paymentState belong to a different billing API.
        expiry_ms = int(result.get("validUntilTimestampMsec", 0))
        initiation_ms = int(result.get("initiationTimestampMsec", 0))
    except (TypeError, ValueError) as exc:
        raise BazaarVerificationError("پاسخ تأیید کافه‌بازار ساختار معتبر ندارد.") from exc
    now_ms = int(time.time() * 1000)
    if initiation_ms <= 0 or expiry_ms <= now_ms or expiry_ms <= initiation_ms:
        raise BazaarVerificationError("اشتراک در کافه‌بازار معتبر یا فعال نیست.")
    return {
        "expires_at": timezone.datetime.fromtimestamp(expiry_ms / 1000, tz=timezone.get_current_timezone()),
        "auto_renewing": bool(result.get("autoRenewing", False)),
        "bazaar_order_id": str(result.get("orderId", ""))[:160],
    }
