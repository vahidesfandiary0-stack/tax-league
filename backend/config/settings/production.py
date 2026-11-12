"""Production-only security settings.

Run with DJANGO_SETTINGS_MODULE=config.settings.production.
Never use this module for local development without the required environment.
"""
import os

from .base import *  # noqa: F403

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "").strip()
if len(SECRET_KEY) < 50 or SECRET_KEY == "unsafe-development-key-change-me":
    raise RuntimeError("DJANGO_SECRET_KEY must be a unique secret of at least 50 characters.")

if DEBUG:
    raise RuntimeError("DJANGO_DEBUG must be false in production.")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required in production.")
if not DATABASE_URL.startswith(("postgres://", "postgresql://")):
    raise RuntimeError("Production DATABASE_URL must use PostgreSQL.")

raw_allowed_hosts = os.getenv("DJANGO_ALLOWED_HOSTS", "").strip()
if not raw_allowed_hosts or "*" in ALLOWED_HOSTS:
    raise RuntimeError("Set explicit DJANGO_ALLOWED_HOSTS values in production.")
if any(host in {"localhost", "127.0.0.1"} for host in ALLOWED_HOSTS):
    raise RuntimeError("Production DJANGO_ALLOWED_HOSTS must contain deployment hostnames, not localhost.")

# Basic authentication is disabled: credentials must never be sent through API Basic Auth.
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = [
    "rest_framework.authentication.TokenAuthentication",
    "rest_framework.authentication.SessionAuthentication",
]

SECURE_SSL_REDIRECT = os.getenv("DJANGO_SECURE_SSL_REDIRECT", "true").lower() == "true"
if not SECURE_SSL_REDIRECT:
    raise RuntimeError("HTTPS redirect must remain enabled in production.")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000"))
if SECURE_HSTS_SECONDS < 1:
    raise RuntimeError("HSTS must be enabled in production after HTTPS is configured.")
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("DJANGO_HSTS_INCLUDE_SUBDOMAINS", "false").lower() == "true"
SECURE_HSTS_PRELOAD = os.getenv("DJANGO_HSTS_PRELOAD", "false").lower() == "true"

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("DJANGO_CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
CORS_ALLOW_ALL_ORIGINS = False

# Uploaded payment receipts must never be served by a public web/static route.
# Keep MEDIA_ROOT on a private volume and serve receipts only through the authenticated API.
FILE_UPLOAD_PERMISSIONS = 0o600
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o700
DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
