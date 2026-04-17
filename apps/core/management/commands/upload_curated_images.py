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
    # Clean modern medical setting — works as full-bleed hero backdrop.
    "hero_background": {
        "url": _u("photo-1631217868264-e5b90bb7e133", 2000, 1200),
        "caption": "Clean modern clinic / pharmacy-style medical setting",
    },

    # ----- Specialty areas (slug → photo) -----
    # Each URL has been re-selected from Unsplash's healthcare collection.
    # Public IDs in Cloudinary are kept the same (expertise/<slug>), so the
    # admin can swap individual images without any code change.
    "endometriozis": {
        # Gentle woman-centered wellness photograph.
        "url": _u("photo-1584515933487-779824d29309", 1600),
        "caption": "Woman wellness — gynecology consultation tone",
    },
    "laparoskopik-cerrahi": {
        # Surgeons in OR performing laparoscopy.
        "url": _u("photo-1629909615184-74f495363b67", 1600),
        "caption": "Laparoscopic surgery in operating room",
    },
    "robotik-cerrahi": {
        # Advanced medical technology — instruments and equipment.
        "url": _u("photo-1579684385127-1ef15d508118", 1600),
        "caption": "Modern medical technology / surgical equipment",
    },
    "vnotes-izsiz-vajinal-cerrahi": {
        # Sterile OR instruments close-up.
        "url": _u("photo-1579165466741-7f35e4755660", 1600),
        "caption": "Sterile operating room tray",
    },
    "uroginekoloji": {
        # Woman with doctor — pelvic health / consultation context.
        "url": _u("photo-1631217868264-e5b90bb7e133", 1600),
        "caption": "Urogynecology consultation",
    },
    "menopoz-yonetimi": {
        # Calm mature woman — menopause / wellness tone.
        "url": _u("photo-1559595500-e15296bdbb48", 1600),
        "caption": "Mature woman — calm wellness tone",
    },
    "jinekolojik-onkoloji": {
        # Microscope / laboratory diagnostics.
        "url": _u("photo-1582719471384-894fbb16e074", 1600),
        "caption": "Laboratory microscope — diagnostics",
    },
    "gebelik-takibi": {
        # Pregnancy ultrasound / prenatal care.
        "url": _u("photo-1544027993-37dbfe43562a", 1600),
        "caption": "Pregnancy ultrasound / prenatal monitoring",
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
