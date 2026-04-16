"""Stub models — fully implemented in Phase 2."""
from django.db import models


class DoctorProfile(models.Model):
    full_name = models.CharField(max_length=200, default="Op. Dr. Savaş Gündoğan")

    class Meta:
        verbose_name = "Doktor Profili"
        verbose_name_plural = "Doktor Profili"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.full_name


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=120, default="Op. Dr. Savaş Gündoğan")

    class Meta:
        verbose_name = "Site Ayarları"
        verbose_name_plural = "Site Ayarları"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.site_name


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "İletişim Mesajı"
        verbose_name_plural = "İletişim Mesajları"

    def __str__(self):
        return f"{self.name} — {self.email}"
