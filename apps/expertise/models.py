"""Clinical specialty areas displayed on /uzmanlik/."""
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class SpecialtyCategory(models.Model):
    name = models.CharField(_("Kategori Adı"), max_length=160)
    slug = models.SlugField(_("Slug"), unique=True, max_length=160)
    icon = models.CharField(
        _("Lucide Icon Adı"), max_length=80, blank=True,
        help_text=_("Örn: 'heart-pulse', 'stethoscope'"),
    )
    order = models.PositiveIntegerField(_("Sıra"), default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Uzmanlık Kategorisi")
        verbose_name_plural = _("Uzmanlık Kategorileri")

    def __str__(self):
        return self.name


class SpecialtyArea(models.Model):
    category = models.ForeignKey(
        SpecialtyCategory,
        null=True, blank=True,
        related_name="areas",
        on_delete=models.SET_NULL,
        verbose_name=_("Kategori"),
    )
    title = models.CharField(_("Başlık"), max_length=200)
    slug = models.SlugField(_("Slug"), unique=True, max_length=200)
    icon = models.CharField(_("Lucide Icon"), max_length=80, blank=True)
    short_description = models.CharField(
        _("Kısa Açıklama"),
        max_length=240,
        help_text=_("Maksimum ~240 karakter — kart için."),
    )
    full_description = RichTextField(_("Detaylı Açıklama"), blank=True)
    symptoms = RichTextField(_("Belirtiler"), blank=True)
    treatment_approach = RichTextField(_("Tedavi Yaklaşımım"), blank=True)
    recovery_info = RichTextField(_("İyileşme Süreci"), blank=True)
    hero_image = CloudinaryField(
        _("Kapak Görseli"), blank=True, null=True, folder="expertise",
        help_text=_("Sitede görünür: Uzmanlık alanları liste kartı ve bu uzmanlık alanı detay sayfasının üst görseli. Ana sayfada öne çıkan kartlarda da kullanılır."),
    )
    order = models.PositiveIntegerField(_("Sıra"), default=0)
    is_featured = models.BooleanField(_("Öne Çıkan"), default=False)
    bento_size = models.CharField(
        _("Bento Kart Boyutu"),
        max_length=10,
        choices=[
            ("1x1", "1x1 — Orta"),
            ("2x1", "2x1 — Geniş"),
            ("1x2", "1x2 — Uzun"),
            ("2x2", "2x2 — Büyük"),
        ],
        default="1x1",
    )
    meta_title = models.CharField(_("Meta Başlık"), max_length=200, blank=True)
    meta_description = models.TextField(_("Meta Açıklama"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = _("Uzmanlık Alanı")
        verbose_name_plural = _("Uzmanlık Alanları")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("expertise:detail", kwargs={"slug": self.slug})
