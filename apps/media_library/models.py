"""Video library — Instagram Reels, YouTube, Acıbadem uploads."""
from cloudinary.models import CloudinaryField
from django.db import models
from django.utils.translation import gettext_lazy as _


class VideoCategory(models.Model):
    name = models.CharField(_("Kategori Adı"), max_length=120)
    slug = models.SlugField(_("Slug"), unique=True, max_length=120)
    order = models.PositiveIntegerField(_("Sıra"), default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Video Kategorisi")
        verbose_name_plural = _("Video Kategorileri")

    def __str__(self):
        return self.name


class Video(models.Model):
    PLATFORM_CHOICES = [
        ("instagram", _("Instagram Reel")),
        ("youtube", _("YouTube")),
        ("youtube_short", _("YouTube Short")),
        ("acibadem", _("Acıbadem Resmi")),
    ]

    title = models.CharField(_("Başlık"), max_length=220)
    description = models.TextField(_("Açıklama"), blank=True)
    platform = models.CharField(
        _("Platform"), max_length=20, choices=PLATFORM_CHOICES, default="instagram"
    )
    video_url = models.URLField(_("Video URL"))
    embed_code = models.TextField(
        _("Özel Embed Kodu"),
        blank=True,
        help_text=_("Varsa buraya iframe HTML'i yapıştırın."),
    )
    thumbnail = CloudinaryField(
        _("Kapak Görseli"), blank=True, null=True, folder="videos",
        help_text=_("Sitede görünür: Videolar sayfasındaki video kartı küçük resmi (thumbnail). Ana sayfa video bölümünde öne çıkanlarda da kullanılır."),
    )
    category = models.ForeignKey(
        VideoCategory,
        null=True, blank=True,
        related_name="videos",
        on_delete=models.SET_NULL,
        verbose_name=_("Kategori"),
    )
    is_featured = models.BooleanField(_("Öne Çıkan"), default=False)
    is_official_acibadem = models.BooleanField(
        _("Acıbadem Resmi Hesabında Yayınlandı"), default=False
    )
    publish_date = models.DateField(_("Yayın Tarihi"), blank=True, null=True)
    order = models.PositiveIntegerField(_("Sıra"), default=0)
    view_count_manual = models.PositiveIntegerField(
        _("İzlenme Sayısı (manuel)"), default=0, blank=True
    )

    class Meta:
        ordering = ["-is_featured", "order", "-publish_date"]
        verbose_name = _("Video")
        verbose_name_plural = _("Videolar")

    def __str__(self):
        return self.title

    @property
    def youtube_id(self) -> str:
        """Extract the YouTube video id from video_url (empty if not YouTube)."""
        if self.platform not in ("youtube", "youtube_short"):
            return ""
        url = self.video_url or ""
        if "youtu.be/" in url:
            return url.split("youtu.be/")[-1].split("?")[0].split("/")[0]
        if "watch?v=" in url:
            return url.split("watch?v=")[-1].split("&")[0]
        if "/shorts/" in url:
            return url.split("/shorts/")[-1].split("?")[0].split("/")[0]
        if "/embed/" in url:
            return url.split("/embed/")[-1].split("?")[0].split("/")[0]
        return ""

    @property
    def embed_url(self) -> str:
        """Return a safe iframe src URL for the video."""
        if self.embed_code:
            return ""  # Consumer should use embed_code directly
        url = self.video_url or ""
        if self.platform == "instagram" and "/reel/" in url:
            reel_id = url.rstrip("/").split("/reel/")[-1].split("/")[0]
            return f"https://www.instagram.com/reel/{reel_id}/embed"
        vid = self.youtube_id
        if vid:
            # youtube-nocookie + parameters for reliable inline playback
            return (
                f"https://www.youtube-nocookie.com/embed/{vid}"
                f"?rel=0&modestbranding=1&playsinline=1"
            )
        return url

    @property
    def thumbnail_url(self) -> str:
        """Effective preview image URL.
        Priority: manually uploaded Cloudinary thumbnail →
                  YouTube auto-thumbnail (hqdefault) → empty string.
        For Instagram reels we cannot derive a thumbnail without the Graph API
        so the template should fall back to showing the iframe or a gradient.
        """
        if self.thumbnail:
            try:
                return self.thumbnail.url
            except Exception:
                pass
        vid = self.youtube_id
        if vid:
            return f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
        return ""
