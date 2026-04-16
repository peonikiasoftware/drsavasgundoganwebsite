"""
Base Django settings shared by dev and prod.

Secrets are read from environment variables only (see .env / .env.example).
Environment-specific overrides live in dev.py and prod.py.
"""
from pathlib import Path

import environ

# ---------------------------------------------------------------------------
# Paths / env
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    EMAIL_USE_TLS=(bool, True),
)

# Read .env from the project root if it exists (dev convenience).
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY", default="unsafe-default-change-me")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

ADMIN_URL_PATH = env("ADMIN_URL_PATH", default="admin/")

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "modeltranslation",  # must be before django.contrib.admin
    "jazzmin",           # must be before django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    "widget_tweaks",
    "ckeditor",
    "ckeditor_uploader",
    "django_htmx",
    "cloudinary",
    "cloudinary_storage",
]

LOCAL_APPS = [
    "apps.core",
    "apps.experience",
    "apps.expertise",
    "apps.publications",
    "apps.media_library",
    "apps.blog",
    "apps.faq",
    "apps.doctor_admin",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise is inserted here only in prod settings.
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # i18n middleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "apps.core.middleware.AnalyticsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "apps.core.context_processors.site_globals",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Database — default SQLite; overridden in prod.py
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("tr", "Türkçe"),
    ("en", "English"),
]

MODELTRANSLATION_DEFAULT_LANGUAGE = "tr"
MODELTRANSLATION_LANGUAGES = ("tr", "en")
MODELTRANSLATION_FALLBACK_LANGUAGES = ("tr",)
MODELTRANSLATION_TRANSLATION_FILES = ()

LOCALE_PATHS = [BASE_DIR / "locale"]

# ---------------------------------------------------------------------------
# Static & Media
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# ---------------------------------------------------------------------------
# Email (overridden per environment)
# ---------------------------------------------------------------------------
EMAIL_HOST = env("EMAIL_HOST", default="")
_email_port_raw = env("EMAIL_PORT", default="587") or "587"
EMAIL_PORT = int(_email_port_raw)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
_email_use_tls_raw = str(env("EMAIL_USE_TLS", default="True")).strip().lower()
EMAIL_USE_TLS = _email_use_tls_raw in ("1", "true", "yes", "on")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@localhost")
CONTACT_NOTIFICATION_EMAIL = env(
    "CONTACT_NOTIFICATION_EMAIL", default="mrtemroztrk@gmail.com"
)

# ---------------------------------------------------------------------------
# Authentication / Sessions
# ---------------------------------------------------------------------------
LOGIN_URL = "/doctor-admin/login/"
LOGIN_REDIRECT_URL = "/doctor-admin/"
LOGOUT_REDIRECT_URL = "/"

# ---------------------------------------------------------------------------
# CKEditor
# ---------------------------------------------------------------------------
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Custom",
        "toolbar_Custom": [
            ["Bold", "Italic", "Underline"],
            ["NumberedList", "BulletedList", "-", "Outdent", "Indent"],
            ["JustifyLeft", "JustifyCenter", "JustifyRight"],
            ["Link", "Unlink", "Anchor"],
            ["Format", "Styles"],
            ["RemoveFormat", "Source"],
        ],
        "height": 320,
        "width": "100%",
    },
    "doctor": {
        "toolbar": "Simple",
        "toolbar_Simple": [
            ["Bold", "Italic", "Underline"],
            ["NumberedList", "BulletedList"],
            ["Link", "Unlink"],
            ["RemoveFormat"],
        ],
        "height": 260,
        "width": "100%",
    },
}

# ---------------------------------------------------------------------------
# Jazzmin
# ---------------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "Dr. Savaş Gündoğan — Yönetim",
    "site_header": "Op. Dr. Savaş Gündoğan",
    "site_brand": "Admin",
    "welcome_sign": "Hoş geldin, yönetici.",
    "copyright": "Op. Dr. Savaş Gündoğan",
    "search_model": ["expertise.SpecialtyArea", "blog.BlogPost", "publications.Publication"],
    "topmenu_links": [
        {"name": "Siteyi Görüntüle", "url": "/", "new_window": True},
        {"name": "Doktor Paneli", "url": "/doctor-admin/", "permissions": ["auth.view_user"]},
    ],
    "icons": {
        "auth.User": "fas fa-user-shield",
        "auth.Group": "fas fa-users",
        "core.DoctorProfile": "fas fa-user-md",
        "core.SiteSettings": "fas fa-cogs",
        "core.ContactMessage": "fas fa-envelope",
        "experience.Education": "fas fa-graduation-cap",
        "experience.Experience": "fas fa-briefcase-medical",
        "experience.Membership": "fas fa-id-card",
        "expertise.SpecialtyArea": "fas fa-stethoscope",
        "expertise.SpecialtyCategory": "fas fa-folder-tree",
        "publications.Publication": "fas fa-book-medical",
        "media_library.Video": "fas fa-video",
        "media_library.VideoCategory": "fas fa-folder",
        "blog.BlogPost": "fas fa-newspaper",
        "blog.BlogCategory": "fas fa-tags",
        "faq.FAQItem": "fas fa-question-circle",
        "faq.FAQCategory": "fas fa-list",
    },
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    "related_modal_active": True,
    "custom_css": "css/admin-custom.css",
    "language_chooser": True,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "dark_mode_theme": "darkly",
    "navbar_small_text": False,
    "accent": "accent-teal",
    "navbar": "navbar-white navbar-light",
    "brand_colour": "navbar-white",
    "sidebar": "sidebar-light-primary",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
