"""Upload curated, medically-relevant, copyright-safe images to Cloudinary
and assign them to the appropriate DB fields.

All photos sourced from Unsplash (Free License — free commercial use,
attribution not required). Each URL points to a Unsplash CDN photo
whose topic matches the target specialty.

Re-running is safe:
- Uploads overwrite the existing public_id (same slot, new image).
- DB assignment only fills empty fields, never replaces a field the
  doctor has already customized.

Run:
    python manage.py upload_curated_images
"""
from __future__ import annotations

import cloudinary
import cloudinary.uploader
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.models import DoctorProfile
from apps.expertise.models import SpecialtyArea


def _u(photo_id: str, w: int = 1600, h: int | None = None) -> str:
    base = f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w={w}&q=80"
    if h:
        base += f"&h={h}"
    return base


# --------------------------------------------------------------
# Curated Unsplash photo IDs. Each chosen to be clean, professional,
# and on-topic. Fallback: if an individual upload fails, we skip it.
# --------------------------------------------------------------
CURATED = {
    # ----- Site-wide -----
    "hero_background": {
        "url": _u("photo-1516549655169-df83a0774514", 2000, 1200),
        "caption": "Modern clinic interior — soft, professional",
    },

    # ----- Specialty areas (slug → photo) -----
    "endometriozis": {
        "url": _u("photo-1594824476967-48c8b964273f", 1600),
        "caption": "Women's health consultation",
    },
    "laparoskopik-cerrahi": {
        "url": _u("photo-1551076805-e1869033e561", 1600),
        "caption": "Operating theatre — surgical focus",
    },
    "robotik-cerrahi": {
        "url": _u("photo-1551190822-a9333d879b1f", 1600),
        "caption": "Modern medical technology",
    },
    "vnotes-izsiz-vajinal-cerrahi": {
        "url": _u("photo-1504813184591-01572f98c85f", 1600),
        "caption": "Sterile instruments, clinical precision",
    },
    "uroginekoloji": {
        "url": _u("photo-1506126613408-eca07ce68773", 1600),
        "caption": "Women's wellness & pelvic health",
    },
    "menopoz-yonetimi": {
        "url": _u("photo-1573496359142-b8d87734a5a2", 1600),
        "caption": "Calm, confident mature woman",
    },
    "jinekolojik-onkoloji": {
        "url": _u("photo-1579165466741-7f35e4755660", 1600),
        "caption": "Microscopy / laboratory diagnostics",
    },
    "gebelik-takibi": {
        "url": _u("photo-1584515933487-779824d29309", 1600),
        "caption": "Prenatal ultrasound / pregnancy care",
    },
}


class Command(BaseCommand):
    help = "Upload curated copyright-safe medical images to Cloudinary + assign to DB."

    def handle(self, *args, **opts):
        cfg = getattr(settings, "CLOUDINARY_STORAGE", None) or {}
        cloud = cfg.get("CLOUD_NAME")
        if not cloud:
            self.stdout.write(self.style.ERROR(
                "Cloudinary not configured — aborting."
            ))
            return

        cloudinary.config(
            cloud_name=cloud,
            api_key=cfg.get("API_KEY", ""),
            api_secret=cfg.get("API_SECRET", ""),
            secure=True,
        )

        uploaded: dict[str, str] = {}
        for key, item in CURATED.items():
            folder_slot = self._folder_slot(key)
            public_id = f"{folder_slot}"
            try:
                resp = cloudinary.uploader.upload(
                    item["url"],
                    public_id=public_id,
                    overwrite=True,
                    invalidate=True,
                    resource_type="image",
                )
                uploaded[key] = resp.get("public_id", public_id)
                self.stdout.write(self.style.SUCCESS(
                    f"  [ok] uploaded {key} → {public_id}  ({item['caption']})"
                ))
            except Exception as exc:  # noqa: BLE001
                self.stdout.write(self.style.WARNING(
                    f"  [skip] {key}: {exc.__class__.__name__}: {str(exc)[:140]}"
                ))

        # -----------------------------------------------------------
        # Assign to DoctorProfile (hero_background) if currently empty
        # -----------------------------------------------------------
        doctor = DoctorProfile.load()
        if not doctor.hero_background and "hero_background" in uploaded:
            doctor.hero_background = uploaded["hero_background"]
            doctor.save(update_fields=["hero_background"])
            self.stdout.write(self.style.SUCCESS(
                "  [ok] DoctorProfile.hero_background assigned"
            ))

        # -----------------------------------------------------------
        # Assign to each SpecialtyArea by slug (only if empty)
        # -----------------------------------------------------------
        assigned = 0
        for area in SpecialtyArea.objects.all():
            pid = uploaded.get(area.slug)
            if pid and not area.hero_image:
                area.hero_image = pid
                area.save(update_fields=["hero_image"])
                self.stdout.write(self.style.SUCCESS(
                    f"  [ok] SpecialtyArea '{area.slug}' hero_image set"
                ))
                assigned += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Uploaded {len(uploaded)} images, assigned {assigned} to specialties."
        ))

    @staticmethod
    def _folder_slot(key: str) -> str:
        """Map the curated key to a Cloudinary public_id with folder."""
        if key == "hero_background":
            return "doctor/hero_background"
        # specialty slugs
        return f"expertise/{key}"
