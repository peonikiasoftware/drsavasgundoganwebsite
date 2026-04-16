"""
Upload Unsplash placeholder images to Cloudinary and assign them to any
CloudinaryField that is currently empty.

Idempotent:
- If Cloudinary upload fails, we log + continue.
- Fields that already have a value are never overwritten — so the doctor's
  real uploaded photos are safe.
"""
from __future__ import annotations

import cloudinary
import cloudinary.uploader
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.models import DoctorProfile
from apps.expertise.models import SpecialtyArea


# ---------------------------------------------------------------------------
# Unsplash source URLs — generic medical/wellness photography. Each is a
# stable Unsplash photo CDN URL sized to ~1600px.
# ---------------------------------------------------------------------------
def _un(photo_id: str, w: int = 1600) -> str:
    return f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w={w}&q=80"


PLACEHOLDERS = {
    "doctor_portrait":      _un("photo-1622253692010-333f2da6031d", 1200),
    "hero_background":      _un("photo-1631815588090-d4bfec5b1ccb", 2000),

    # Specialty slugs map directly to SpecialtyArea.slug values.
    "endometriozis":        _un("photo-1559757148-5c350d0d3c56"),
    "laparoskopik-cerrahi": _un("photo-1579684385127-1ef15d508118"),
    "robotik-cerrahi":      _un("photo-1581090700227-1e37b190418e"),
    "vnotes-izsiz-vajinal-cerrahi": _un("photo-1612277795421-9bc7706a4a34"),
    "uroginekoloji":        _un("photo-1584515933487-779824d29309"),
    "menopoz-yonetimi":     _un("photo-1518621736915-f3b1c41bfd00"),
    "jinekolojik-onkoloji": _un("photo-1530026405186-ed1f139313f8"),
    "gebelik-takibi":       _un("photo-1519824145371-296894a0daa9"),
}


class Command(BaseCommand):
    help = "Seed placeholder images from Unsplash → Cloudinary (idempotent)."

    def handle(self, *args, **opts):
        cfg = getattr(settings, "CLOUDINARY_STORAGE", None) or {}
        cloud = cfg.get("CLOUD_NAME")
        if not cloud:
            self.stdout.write(self.style.WARNING(
                "Cloudinary not configured — skipping placeholder upload."
            ))
            return

        cloudinary.config(
            cloud_name=cloud,
            api_key=cfg.get("API_KEY", ""),
            api_secret=cfg.get("API_SECRET", ""),
            secure=True,
        )

        # Track what got uploaded this run
        uploaded: dict[str, str] = {}
        for key, url in PLACEHOLDERS.items():
            public_id = f"placeholders/{key}"
            try:
                resp = cloudinary.uploader.upload(
                    url,
                    public_id=public_id,
                    overwrite=True,
                    invalidate=True,
                    resource_type="image",
                )
                uploaded[key] = resp.get("public_id", public_id)
                self.stdout.write(f"  [ok]uploaded {key}")
            except Exception as exc:  # noqa: BLE001
                self.stdout.write(self.style.WARNING(
                    f"  [fail] {key}: {exc.__class__.__name__}: {str(exc)[:160]}"
                ))

        # ----------------------------------------------------------
        # Assign to DoctorProfile (only if currently empty)
        # ----------------------------------------------------------
        doctor = DoctorProfile.load()
        changed = False
        if not doctor.portrait_photo and "doctor_portrait" in uploaded:
            doctor.portrait_photo = uploaded["doctor_portrait"]
            changed = True
        if not doctor.hero_background and "hero_background" in uploaded:
            doctor.hero_background = uploaded["hero_background"]
            changed = True
        if changed:
            doctor.save()
            self.stdout.write("  [ok]DoctorProfile placeholders set")

        # ----------------------------------------------------------
        # Assign to each SpecialtyArea by slug (only if empty)
        # ----------------------------------------------------------
        for area in SpecialtyArea.objects.all():
            pid = uploaded.get(area.slug)
            if pid and not area.hero_image:
                area.hero_image = pid
                area.save(update_fields=["hero_image"])
                self.stdout.write(f"  [ok]SpecialtyArea '{area.slug}' image set")

        self.stdout.write(self.style.SUCCESS("Placeholder seed complete."))
