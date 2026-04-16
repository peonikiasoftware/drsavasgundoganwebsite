"""Education, Experience and Membership models for the Kariyer page."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Education(models.Model):
    institution = models.CharField(_("Kurum"), max_length=200)
    degree = models.CharField(_("Derece"), max_length=160)
    field = models.CharField(_("Alan"), max_length=160, blank=True)
    location = models.CharField(_("Konum"), max_length=160, blank=True)
    year_start = models.PositiveIntegerField(_("Başlangıç Yılı"))
    year_end = models.PositiveIntegerField(_("Bitiş Yılı"), blank=True, null=True)
    description = models.TextField(_("Açıklama"), blank=True)
    order = models.PositiveIntegerField(_("Sıra"), default=0)
    is_highlight = models.BooleanField(_("Ana Sayfa Öne Çıkan"), default=False)

    class Meta:
        ordering = ["-year_start", "order"]
        verbose_name = _("Eğitim")
        verbose_name_plural = _("Eğitim")

    def __str__(self):
        return f"{self.degree} — {self.institution} ({self.year_start}–{self.year_end or '…'})"


class Experience(models.Model):
    position = models.CharField(_("Pozisyon"), max_length=200)
    institution = models.CharField(_("Kurum"), max_length=200)
    location = models.CharField(_("Konum"), max_length=160, blank=True)
    year_start = models.PositiveIntegerField(_("Başlangıç Yılı"))
    year_end = models.PositiveIntegerField(_("Bitiş Yılı"), blank=True, null=True)
    is_current = models.BooleanField(_("Devam Ediyor"), default=False)
    description = models.TextField(_("Açıklama"), blank=True)
    order = models.PositiveIntegerField(_("Sıra"), default=0)
    is_highlight = models.BooleanField(_("Ana Sayfa Öne Çıkan"), default=False)

    class Meta:
        ordering = ["-year_start", "order"]
        verbose_name = _("Deneyim")
        verbose_name_plural = _("Deneyim")

    def __str__(self):
        return f"{self.position} — {self.institution}"


class Membership(models.Model):
    name = models.CharField(_("Dernek / Kuruluş Adı"), max_length=200)
    url = models.URLField(_("URL"), blank=True)
    year_joined = models.PositiveIntegerField(
        _("Katılım Yılı"), blank=True, null=True
    )
    order = models.PositiveIntegerField(_("Sıra"), default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Üyelik")
        verbose_name_plural = _("Üyelikler")

    def __str__(self):
        return self.name
