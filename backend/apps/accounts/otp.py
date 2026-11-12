import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import OTPChallenge


OTP_TTL_SECONDS = 180
OTP_MAX_ATTEMPTS = 5


def digest_code(phone_number, code):
    key = settings.SECRET_KEY.encode("utf-8")
    message = f"{phone_number}:{code}".encode("utf-8")
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def issue_challenge(phone_number, request_ip=None):
    # Invalidate outstanding codes before issuing a new challenge.
    OTPChallenge.objects.filter(
        phone_number=phone_number, consumed_at__isnull=True
    ).update(consumed_at=timezone.now())

    code = f"{secrets.randbelow(1_000_000):06d}"
    challenge = OTPChallenge.objects.create(
        phone_number=phone_number,
        code_digest=digest_code(phone_number, code),
        expires_at=timezone.now() + timedelta(seconds=OTP_TTL_SECONDS),
        request_ip=request_ip,
    )
    return challenge, code


def verify_challenge(phone_number, code):
    challenge = (
        OTPChallenge.objects.filter(phone_number=phone_number, consumed_at__isnull=True)
        .order_by("-created_at")
        .first()
    )
    if not challenge or not challenge.is_valid:
        return False
    challenge.attempts += 1
    valid = hmac.compare_digest(challenge.code_digest, digest_code(phone_number, code))
    if valid:
        challenge.consumed_at = timezone.now()
    challenge.save(update_fields=["attempts", "consumed_at"])
    return valid
