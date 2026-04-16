"""Development settings — DEBUG on, SQLite, console email, local media."""
from .base import *  # noqa: F401,F403
from .base import BASE_DIR, MIDDLEWARE, INSTALLED_APPS, env

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Email → console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable Cloudinary in dev unless credentials are provided; fall back to local FS.
if not env("CLOUDINARY_CLOUD_NAME", default=""):
    # Remove cloudinary_storage to avoid auth errors when uploading
    if "cloudinary_storage" in INSTALLED_APPS:
        INSTALLED_APPS = [a for a in INSTALLED_APPS if a != "cloudinary_storage"]
        INSTALLED_APPS.append("cloudinary_storage")  # keep registered but no default backend
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
else:
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": env("CLOUDINARY_CLOUD_NAME"),
        "API_KEY": env("CLOUDINARY_API_KEY", default=""),
        "API_SECRET": env("CLOUDINARY_API_SECRET", default=""),
    }

# Debug toolbar (optional; only if installed)
try:
    import debug_toolbar  # noqa: F401
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1"]
except ImportError:
    pass

# Secure-defaults OFF in dev
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
