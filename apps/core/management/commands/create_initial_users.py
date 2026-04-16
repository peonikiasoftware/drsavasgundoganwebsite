"""Create the superuser (Murat) and the doctor editor (Savaş)."""
from __future__ import annotations

import os

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

DOCTOR_GROUP_NAME = "doctor_editors"

# Models that the doctor group can edit (change). They should not touch
# auth/groups/users, site settings, or site-wide content rules.
DOCTOR_PERMISSIONS = {
    ("core", "doctorprofile"): ("view", "change"),
    ("core", "contactmessage"): ("view", "change"),
    ("experience", "education"): ("view", "add", "change", "delete"),
    ("experience", "experience"): ("view", "add", "change", "delete"),
    ("experience", "membership"): ("view", "add", "change", "delete"),
    ("expertise", "specialtycategory"): ("view",),
    ("expertise", "specialtyarea"): ("view", "add", "change"),
    ("publications", "publication"): ("view", "add", "change", "delete"),
    ("media_library", "videocategory"): ("view",),
    ("media_library", "video"): ("view", "add", "change", "delete"),
    ("blog", "blogcategory"): ("view",),
    ("blog", "blogpost"): ("view", "add", "change", "delete"),
    ("faq", "faqcategory"): ("view",),
    ("faq", "faqitem"): ("view", "add", "change", "delete"),
}


def _get_perm(app_label: str, model: str, action: str) -> Permission | None:
    try:
        ct = ContentType.objects.get(app_label=app_label, model=model)
    except ContentType.DoesNotExist:
        return None
    codename = f"{action}_{model}"
    return Permission.objects.filter(content_type=ct, codename=codename).first()


class Command(BaseCommand):
    help = "Seed the initial superuser + doctor-editor user from env vars."

    def handle(self, *args, **opts):
        group = self._ensure_doctor_group()
        self._ensure_superuser()
        self._ensure_doctor_user(group)

    # ------------------------------------------------------------------
    def _ensure_doctor_group(self) -> Group:
        group, created = Group.objects.get_or_create(name=DOCTOR_GROUP_NAME)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created group '{DOCTOR_GROUP_NAME}'"))
        perms: list[Permission] = []
        for (app_label, model), actions in DOCTOR_PERMISSIONS.items():
            for action in actions:
                p = _get_perm(app_label, model, action)
                if p:
                    perms.append(p)
        group.permissions.set(perms)
        self.stdout.write(self.style.SUCCESS(
            f"Group '{DOCTOR_GROUP_NAME}' updated with {len(perms)} permissions."
        ))
        return group

    def _ensure_superuser(self) -> None:
        username = os.getenv("ADMIN_SUPERUSER_USERNAME")
        email = os.getenv("ADMIN_SUPERUSER_EMAIL", "")
        password = os.getenv("ADMIN_SUPERUSER_PASSWORD")
        if not (username and password):
            self.stdout.write(self.style.WARNING(
                "ADMIN_SUPERUSER_USERNAME / PASSWORD not set — skipping superuser."
            ))
            return
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Superuser '{username}' already exists — skipping.")
            return
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))

    def _ensure_doctor_user(self, group: Group) -> None:
        username = os.getenv("DOCTOR_ADMIN_USERNAME")
        email = os.getenv("DOCTOR_ADMIN_EMAIL", "")
        password = os.getenv("DOCTOR_ADMIN_PASSWORD")
        if not (username and password):
            self.stdout.write(self.style.WARNING(
                "DOCTOR_ADMIN_USERNAME / PASSWORD not set — skipping doctor user."
            ))
            return
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": "Savaş",
                "last_name": "Gündoğan",
                "is_staff": True,
            },
        )
        if created:
            user.set_password(password)
        user.is_staff = True
        user.is_superuser = False
        user.save()
        user.groups.add(group)
        msg = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{msg} doctor user '{username}'."))
