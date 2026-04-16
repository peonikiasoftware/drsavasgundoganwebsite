"""Frequently Asked Questions (accordion)."""
from ckeditor.fields import RichTextField
from django.db import models
from django.utils.translation import gettext_lazy as _


class FAQCategory(models.Model):
    name = models.CharField(_("Kategori Adı"), max_length=160)
    order = models.PositiveIntegerField(_("Sıra"), default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("SSS Kategorisi")
        verbose_name_plural = _("SSS Kategorileri")

    def __str__(self):
        return self.name


class FAQItem(models.Model):
    category = models.ForeignKey(
        FAQCategory,
        null=True, blank=True,
        related_name="items",
        on_delete=models.SET_NULL,
        verbose_name=_("Kategori"),
    )
    question = models.CharField(_("Soru"), max_length=300)
    answer = RichTextField(_("Cevap"))
    related_video = models.ForeignKey(
        "media_library.Video",
        null=True, blank=True,
        related_name="faq_items",
        on_delete=models.SET_NULL,
        verbose_name=_("İlgili Video"),
    )
    related_specialty = models.ForeignKey(
        "expertise.SpecialtyArea",
        null=True, blank=True,
        related_name="faq_items",
        on_delete=models.SET_NULL,
        verbose_name=_("İlgili Uzmanlık"),
    )
    order = models.PositiveIntegerField(_("Sıra"), default=0)
    is_featured = models.BooleanField(_("Öne Çıkan"), default=False)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = _("SSS")
        verbose_name_plural = _("Sıkça Sorulan Sorular")

    def __str__(self):
        return self.question
