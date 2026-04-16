"""Global template context — `doctor`, `site_settings`, `LANGUAGES_LIST`."""
from django.conf import settings


def site_globals(request):
    """Make DoctorProfile + SiteSettings available in every template."""
    from .models import DoctorProfile, SiteSettings

    return {
        "doctor": DoctorProfile.load(),
        "site_settings": SiteSettings.load(),
        "LANGUAGES_LIST": settings.LANGUAGES,
        "CURRENT_YEAR": 2026,
    }
