from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Video, VideoCategory


@admin.register(VideoCategory)
class VideoCategoryAdmin(TabbedTranslationAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Video)
class VideoAdmin(TabbedTranslationAdmin):
    list_display = (
        "title",
        "platform",
        "is_official_acibadem",
        "is_featured",
        "publish_date",
        "order",
    )
    list_editable = ("is_featured", "is_official_acibadem", "order")
    list_filter = ("platform", "is_official_acibadem", "is_featured", "category")
    search_fields = ("title", "description", "video_url")
    fieldsets = (
        (None, {"fields": ("title", "description", "category")}),
        ("Medya", {"fields": ("platform", "video_url", "embed_code", "thumbnail")}),
        ("Gösterim", {
            "fields": (
                "is_featured",
                "is_official_acibadem",
                "publish_date",
                "order",
                "view_count_manual",
            ),
        }),
    )
