"""Private internal testing settings. Never expose this service publicly."""
import os

from .base import *

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "").strip()
if len(SECRET_KEY) < 50:
    raise RuntimeError("A unique DJANGO_SECRET_KEY of at least 50 characters is required.")

if DEBUG:
    raise RuntimeError("DJANGO_DEBUG must remain false.")

if not DATABASE_URL.startswith(("postgres://", "postgresql://")):
    raise RuntimeError("Internal deployment requires PostgreSQL.")

if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:
    raise RuntimeError("Set explicit internal ALLOWED_HOSTS.")
ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS + ["127.0.0.1", "localhost"]))

REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = [
    "rest_framework.authentication.TokenAuthentication",
    "rest_framework.authentication.SessionAuthentication",
]

SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

CSRF_TRUSTED_ORIGINS = []
CORS_ALLOWED_ORIGINS = []
CORS_ALLOW_ALL_ORIGINS = False

FILE_UPLOAD_PERMISSIONS = 0o600
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o700
DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024
