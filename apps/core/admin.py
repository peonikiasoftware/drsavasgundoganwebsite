from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import ContactMessage, DoctorProfile, PageView, SiteSettings


@admin.register(DoctorProfile)
class DoctorProfileAdmin(TabbedTranslationAdmin):
    fieldsets = (
        ("Kimlik", {
            "fields": ("full_name", "title_short", "title_long"),
        }),
        ("Hero", {
            "fields": (
                "hero_headline",
                "hero_subheadline",
                "hero_intro_paragraph",
                "hero_background",
            ),
        }),
        ("Görseller", {
            "fields": ("portrait_photo", "signature_image"),
        }),
        ("Biyografi", {
            "fields": ("bio_short", "bio_long", "philosophy_quote"),
        }),
        ("İletişim", {
            "fields": (
                "email_public",
                "phone_public",
                "appointment_url",
                "hospital_name",
                "hospital_address",
                "google_maps_embed_url",
            ),
        }),
        ("Sosyal Medya", {
            "fields": (
                "instagram_url",
                "instagram_handle",
                "linkedin_url",
                "youtube_url",
                "facebook_url",
                "google_scholar_url",
                "acibadem_profile_tr",
                "acibadem_profile_en",
            ),
        }),
        ("Sayaçlar", {
            "fields": (
                "years_of_experience",
                "publication_count",
                "procedures_count",
            ),
        }),
    )

    def has_add_permission(self, request):
        return not DoctorProfile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(TabbedTranslationAdmin):
    fieldsets = (
        ("Genel", {"fields": ("site_name", "maintenance_mode")}),
        ("SEO", {"fields": ("default_meta_title", "default_meta_description", "default_og_image")}),
        ("Marka / Logo", {
            "fields": ("site_logo", "site_logo_light", "favicon"),
            "description": "Header, footer ve tarayıcı sekmesi için logolar. Boş bırakılırsa 'SG' gradient rozeti fallback olarak kullanılır.",
        }),
        ("Sosyal Medya İkonları", {
            "fields": (
                "social_icon_instagram",
                "social_icon_scholar",
                "social_icon_linkedin",
                "social_icon_youtube",
                "social_icon_facebook",
            ),
            "description": "Her platform için özel ikon (SVG veya PNG). Boşsa Lucide icon fallback gösterilir.",
        }),
        ("Yasal Metinler", {"fields": ("cookie_banner_text", "kvkk_body", "privacy_body")}),
        ("Diğer", {"fields": ("newsletter_enabled", "google_analytics_id")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ("created_at", "path", "language", "device_type", "country", "is_bot")
    list_filter = ("is_bot", "device_type", "language", "country")
    search_fields = ("path", "user_agent", "referrer")
    readonly_fields = (
        "path", "language", "referrer", "user_agent",
        "visitor_hash", "device_type", "is_bot", "country", "created_at",
    )
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "is_read", "is_archived", "created_at")
    list_filter = ("is_read", "is_archived", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at", "ip_address")
    actions = ("mark_as_read", "mark_as_archived")

    @admin.action(description="Okundu olarak işaretle")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="Arşivle")
    def mark_as_archived(self, request, queryset):
        queryset.update(is_archived=True, is_read=True)
