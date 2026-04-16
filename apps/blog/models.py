"""Blog posts (long-form patient education)."""
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class BlogCategory(models.Model):
    name = models.CharField(_("Kategori Adı"), max_length=160)
    slug = models.SlugField(_("Slug"), unique=True, max_length=160)
    description = models.TextField(_("Açıklama"), blank=True)
    order = models.PositiveIntegerField(_("Sıra"), default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Blog Kategorisi")
        verbose_name_plural = _("Blog Kategorileri")

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    STATUS_CHOICES = [
        ("draft", _("Taslak")),
        ("published", _("Yayında")),
        ("archived", _("Arşiv")),
    ]

    title = models.CharField(_("Başlık"), max_length=220)
    slug = models.SlugField(_("Slug"), unique=True, max_length=220)
    category = models.ForeignKey(
        BlogCategory,
        null=True, blank=True,
        related_name="posts",
        on_delete=models.SET_NULL,
        verbose_name=_("Kategori"),
    )
    related_specialty = models.ForeignKey(
        "expertise.SpecialtyArea",
        null=True, blank=True,
        related_name="blog_posts",
        on_delete=models.SET_NULL,
        verbose_name=_("İlgili Uzmanlık Alanı"),
    )
    excerpt = models.TextField(_("Özet"), max_length=320, blank=True)
    content = RichTextField(_("İçerik"))
    featured_image = CloudinaryField(
        _("Kapak Görseli"), blank=True, null=True, folder="blog"
    )
    author_name = models.CharField(
        _("Yazar"), max_length=160, default="Op. Dr. Savaş Gündoğan"
    )
    read_time_minutes = models.PositiveIntegerField(
        _("Okuma Süresi (dk)"), default=5
    )
    status = models.CharField(
        _("Durum"), max_length=16, choices=STATUS_CHOICES, default="draft"
    )
    published_at = models.DateTimeField(_("Yayın Tarihi"), blank=True, null=True)
    meta_title = models.CharField(_("Meta Başlık"), max_length=200, blank=True)
    meta_description = models.TextField(_("Meta Açıklama"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(_("Görüntülenme"), default=0)
    is_featured = models.BooleanField(_("Öne Çıkan"), default=False)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = _("Blog Yazısı")
        verbose_name_plural = _("Blog Yazıları")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})
