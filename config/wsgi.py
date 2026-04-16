"""
WSGI config — Vercel entry point.

Vercel's @vercel/python runtime looks for an `app` or `application` symbol.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_wsgi_application()
app = application  # Vercel convenience alias
