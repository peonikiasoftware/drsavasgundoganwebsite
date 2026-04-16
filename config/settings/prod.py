"""Production settings — Vercel serverless + Supabase Postgres + Cloudinary."""
import dj_database_url

from .base import *  # noqa: F401,F403
from .base import BASE_DIR, MIDDLEWARE, INSTALLED_APPS, env

DEBUG = False

# Vercel's @vercel/static-build serves the contents of `staticfiles_build/`
# at the site root, so `staticfiles_build/static/foo.css` → `/static/foo.css`.
STATIC_ROOT = BASE_DIR / "staticfiles_build" / "static"

ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=[".vercel.app", "drsavasgundogan.com", "www.drsavasgundogan.com"],
)

CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
    "https://drsavasgundogan.com",
    "https://www.drsavasgundogan.com",
]

# ---------------------------------------------------------------------------
# Database — Supabase (Transaction pooler, port 6543)
# Accepts either DATABASE_URL (manual) or POSTGRES_URL (Vercel+Supabase
# marketplace integration auto-sets this name).
# ---------------------------------------------------------------------------
DATABASE_URL = (
    env("DATABASE_URL", default="")
    or env("POSTGRES_URL", default="")
    or env("POSTGRES_PRISMA_URL", default="")
)
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=0,       # Serverless — no persistent connections
            ssl_require=True,
        )
    }

# ---------------------------------------------------------------------------
# Cloudinary (optional — falls back to in-memory null storage if missing,
# so the build doesn't fail when credentials aren't configured yet)
# ---------------------------------------------------------------------------
_cloudinary_cloud = env("CLOUDINARY_CLOUD_NAME", default="")
_cloudinary_key = env("CLOUDINARY_API_KEY", default="")
_cloudinary_secret = env("CLOUDINARY_API_SECRET", default="")

if _cloudinary_cloud and _cloudinary_key and _cloudinary_secret:
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": _cloudinary_cloud,
        "API_KEY": _cloudinary_key,
        "API_SECRET": _cloudinary_secret,
    }
    DEFAULT_MEDIA_BACKEND = "cloudinary_storage.storage.MediaCloudinaryStorage"
else:
    # No Cloudinary configured — use local filesystem. On Vercel this is
    # ephemeral (writes disappear between invocations) but at least the
    # site won't crash when rendering pages that don't actually have
    # any uploaded media yet.
    DEFAULT_MEDIA_BACKEND = "django.core.files.storage.FileSystemStorage"

# ---------------------------------------------------------------------------
# Static files — WhiteNoise
# ---------------------------------------------------------------------------
STORAGES = {
    "default": {"BACKEND": DEFAULT_MEDIA_BACKEND},
    "staticfiles": {
        # Non-manifest: gzip/brotli compress but don't post-process.
        # Jazzmin / third-party apps ship minified JS referencing .map
        # files they don't include; the manifest variant would fail on those.
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Insert WhiteNoise just after SecurityMiddleware
if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

WHITENOISE_MANIFEST_STRICT = False

# ---------------------------------------------------------------------------
# Email — SMTP via Resend / SendGrid
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# Logging — stdout for Vercel
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[{levelname}] {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
