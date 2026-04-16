"""Public-site analytics middleware.

Records one PageView per successful HTML GET request to a public page.
Silent failure — analytics errors must never break rendering.
"""
from __future__ import annotations

import hashlib


BOT_KEYWORDS = (
    "bot", "crawl", "spider", "scrap", "curl/", "wget/", "python-",
    "httpx", "requests/", "postman", "java/", "ahrefs", "semrush",
    "googlebot", "bingbot", "yandex", "duckduck", "facebookexternal",
    "linkedinbot", "whatsapp", "telegrambot", "slackbot",
    "headless", "lighthouse", "pingdom", "uptimerobot",
)

EXCLUDE_PREFIXES = (
    "/admin/", "/doctor-admin/", "/static/", "/media/",
    "/ckeditor/", "/__debug__/", "/robots.txt", "/favicon.ico",
    "/i18n/",
)

HASH_SALT = "drsavas-v1-analytics"


def _client_ip(request) -> str:
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") or ""


def _device_type(ua_lower: str) -> str:
    if any(k in ua_lower for k in BOT_KEYWORDS):
        return "bot"
    if "ipad" in ua_lower or "tablet" in ua_lower:
        return "tablet"
    if "mobile" in ua_lower or "iphone" in ua_lower or "android" in ua_lower:
        return "mobile"
    return "desktop"


class AnalyticsMiddleware:
    """Persists a PageView on successful public HTML GETs."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._maybe_record(request, response)
        except Exception:
            pass  # analytics must never break the site
        return response

    def _maybe_record(self, request, response):
        if request.method != "GET":
            return
        if response.status_code != 200:
            return
        path = request.path or ""
        if any(path.startswith(p) for p in EXCLUDE_PREFIXES):
            return
        content_type = response.get("Content-Type", "")
        if "text/html" not in content_type:
            return

        from .models import PageView  # local import — middleware loads early

        ua = (request.META.get("HTTP_USER_AGENT") or "")[:400]
        ua_lower = ua.lower()
        device = _device_type(ua_lower)
        is_bot = device == "bot"

        ip = _client_ip(request)
        # Hash IP+UA+salt for a privacy-safe visitor fingerprint
        fingerprint = hashlib.sha256(
            f"{ip}|{ua}|{HASH_SALT}".encode("utf-8", errors="ignore")
        ).hexdigest()[:32]

        PageView.objects.create(
            path=path[:500],
            language=getattr(request, "LANGUAGE_CODE", "") or "",
            referrer=(request.META.get("HTTP_REFERER") or "")[:500],
            user_agent=ua,
            visitor_hash=fingerprint,
            device_type=device,
            is_bot=is_bot,
            country=(request.META.get("HTTP_X_VERCEL_IP_COUNTRY") or "")[:4],
        )
