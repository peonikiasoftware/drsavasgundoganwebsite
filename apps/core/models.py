"""Core models: singleton DoctorProfile + SiteSettings + ContactMessage."""
from cloudinary.models import CloudinaryField
from ckeditor.fields import RichTextField
from django.db import models
from django.utils.translation import gettext_lazy as _


class SingletonMixin(models.Model):
    """Mixin that forces pk=1 so only one row of this model ever exists."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # Prevent deletion — this is a singleton

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj


class DoctorProfile(SingletonMixin, models.Model):
    """Core doctor metadata shown across the entire site."""

    # Identity
    full_name = models.CharField(
        _("Tam Ad"), max_length=200, default="Op. Dr. Savaş Gündoğan"
    )
    title_short = models.CharField(_("Kısa Ünvan"), max_length=60, default="Op. Dr.")
    title_long = models.CharField(
        _("Uzun Ünvan"),
        max_length=160,
        default="Kadın Hastalıkları ve Doğum Uzmanı",
    )

    # Hero strings
    hero_headline = models.CharField(
        _("Hero Ana Başlık"),
        max_length=220,
        default="Minimal İnvaziv Jinekolojik Cerrahi ve Kadın Sağlığı",
    )
    hero_subheadline = models.CharField(
        _("Hero Alt Başlık"),
        max_length=260,
        default="Laparoskopi · Robotik Cerrahi · vNOTES · Endometriozis · Ürojinekoloji",
    )
    hero_intro_paragraph = models.TextField(
        _("Hero Paragraf"),
        blank=True,
        help_text=_("Hero bölümünde görünen kısa tanıtım paragrafı."),
    )

    # Visuals
    portrait_photo = CloudinaryField(
        _("Portre Fotoğraf"), blank=True, null=True, folder="doctor"
    )
    hero_background = CloudinaryField(
        _("Hero Arka Plan"), blank=True, null=True, folder="doctor"
    )
    signature_image = CloudinaryField(
        _("İmza Görseli"), blank=True, null=True, folder="doctor"
    )

    # Biography
    bio_short = models.TextField(
        _("Kısa Biyografi"), help_text=_("Yaklaşık 150 kelime."), blank=True
    )
    bio_long = RichTextField(_("Uzun Biyografi"), blank=True)
    philosophy_quote = models.TextField(_("Felsefe Alıntısı"), blank=True)

    # Contact
    email_public = models.EmailField(
        _("Halka Açık E-posta"), default="savas.gundogan@acibadem.com"
    )
    phone_public = models.CharField(_("Telefon"), max_length=40, blank=True)
    appointment_url = models.URLField(
        _("Randevu URL"),
        default="https://www.acibadem.com.tr/doktor/savas-gundogan/",
    )
    hospital_name = models.CharField(
        _("Hastane Adı"), max_length=160, default="Acıbadem Maslak Hastanesi"
    )
    hospital_address = models.TextField(
        _("Hastane Adresi"),
        default="Büyükdere Cad. No:40, 34457 Maslak / İstanbul",
    )
    google_maps_embed_url = models.TextField(_("Google Maps Embed URL"), blank=True)

    # Social
    instagram_url = models.URLField(
        _("Instagram URL"),
        default="https://www.instagram.com/dr.savasgundogan/",
    )
    instagram_handle = models.CharField(
        _("Instagram Kullanıcı Adı"), max_length=60, default="@dr.savasgundogan"
    )
    linkedin_url = models.URLField(_("LinkedIn URL"), blank=True)
    youtube_url = models.URLField(_("YouTube URL"), blank=True)
    facebook_url = models.URLField(_("Facebook URL"), blank=True)
    google_scholar_url = models.URLField(
        _("Google Scholar URL"),
        default="https://scholar.google.com/citations?user=9hUh--8AAAAJ&hl=en",
    )
    acibadem_profile_tr = models.URLField(
        _("Acıbadem Profil (TR)"),
        default="https://www.acibadem.com.tr/doktor/savas-gundogan/",
    )
    acibadem_profile_en = models.URLField(
        _("Acıbadem Profil (EN)"),
        default="https://www.acibadem.com.tr/en/doctor/savas-gundogan/",
    )

    # Counters
    years_of_experience = models.PositiveIntegerField(_("Yıllık Deneyim"), default=12)
    publication_count = models.PositiveIntegerField(_("Yayın Sayısı"), default=20)
    procedures_count = models.PositiveIntegerField(
        _("Prosedür Sayısı"), blank=True, null=True
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Doktor Profili")
        verbose_name_plural = _("Doktor Profili")

    def __str__(self):
        return self.full_name


class SiteSettings(SingletonMixin, models.Model):
    """Global site settings — SEO defaults, analytics, cookie banner."""

    site_name = models.CharField(
        _("Site Adı"), max_length=120, default="Op. Dr. Savaş Gündoğan"
    )
    default_meta_title = models.CharField(
        _("Varsayılan Meta Başlık"), max_length=200, blank=True
    )
    default_meta_description = models.TextField(
        _("Varsayılan Meta Açıklama"), blank=True
    )
    default_og_image = CloudinaryField(
        _("Varsayılan OG Görseli"), blank=True, null=True, folder="site"
    )
    cookie_banner_text = models.TextField(
        _("Çerez Banner Metni"),
        default=(
            "Sitemizde deneyiminizi iyileştirmek için çerezler kullanılmaktadır. "
            "Detaylar için Aydınlatma Metni'ni inceleyebilirsiniz."
        ),
    )
    kvkk_body = RichTextField(_("Aydınlatma Metni İçeriği"), blank=True)
    privacy_body = RichTextField(_("Gizlilik Politikası İçeriği"), blank=True)

    newsletter_enabled = models.BooleanField(_("Bülten Aktif"), default=False)
    google_analytics_id = models.CharField(
        _("Google Analytics ID"), max_length=40, blank=True
    )
    maintenance_mode = models.BooleanField(_("Bakım Modu"), default=False)

    class Meta:
        verbose_name = _("Site Ayarları")
        verbose_name_plural = _("Site Ayarları")

    def __str__(self):
        return self.site_name


class PageView(models.Model):
    """One row per public HTML pageview, recorded by AnalyticsMiddleware.
    No PII stored — only hashed (IP + UA) fingerprint for unique-visitor counts."""

    DEVICE_CHOICES = [
        ("desktop", "Masaüstü"),
        ("mobile", "Mobil"),
        ("tablet", "Tablet"),
        ("bot", "Bot"),
    ]

    path = models.CharField(_("Yol"), max_length=500, db_index=True)
    language = models.CharField(_("Dil"), max_length=8, blank=True)
    referrer = models.TextField(_("Referans"), blank=True)
    user_agent = models.CharField(_("User-Agent"), max_length=400, blank=True)
    visitor_hash = models.CharField(
        _("Ziyaretçi Parmak İzi"), max_length=64, blank=True, db_index=True
    )
    device_type = models.CharField(
        _("Cihaz"), max_length=10, choices=DEVICE_CHOICES, default="desktop"
    )
    is_bot = models.BooleanField(_("Bot mu?"), default=False, db_index=True)
    country = models.CharField(_("Ülke"), max_length=4, blank=True)
    created_at = models.DateTimeField(_("Zaman"), auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Sayfa Görüntüleme")
        verbose_name_plural = _("Sayfa Görüntülemeleri")
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["path", "-created_at"]),
            models.Index(fields=["is_bot", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.path} — {self.created_at:%Y-%m-%d %H:%M}"


class ContactMessage(models.Model):
    """Submissions from the public contact form."""

    name = models.CharField(_("Ad Soyad"), max_length=120)
    email = models.EmailField(_("E-posta"))
    phone = models.CharField(_("Telefon"), max_length=40, blank=True)
    subject = models.CharField(_("Konu"), max_length=160, blank=True)
    message = models.TextField(_("Mesaj"))
    kvkk_consent = models.BooleanField(_("KVKK Onayı"), default=False)
    is_read = models.BooleanField(_("Okundu"), default=False)
    is_archived = models.BooleanField(_("Arşivlendi"), default=False)
    ip_address = models.GenericIPAddressField(
        _("IP Adresi"), blank=True, null=True
    )
    created_at = models.DateTimeField(_("Oluşturulma"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("İletişim Mesajı")
        verbose_name_plural = _("İletişim Mesajları")

    def __str__(self):
        return f"{self.name} <{self.email}> — {self.created_at:%Y-%m-%d}"
