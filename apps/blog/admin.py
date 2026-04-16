from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import BlogCategory, BlogPost


@admin.register(BlogCategory)
class BlogCategoryAdmin(TabbedTranslationAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlogPost)
class BlogPostAdmin(TabbedTranslationAdmin):
    list_display = (
        "title",
        "category",
        "status",
        "published_at",
        "is_featured",
        "view_count",
    )
    list_filter = ("status", "category", "is_featured")
    list_editable = ("status", "is_featured")
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"

    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "related_specialty", "status", "published_at")}),
        ("İçerik", {"fields": ("excerpt", "content", "featured_image")}),
        ("Meta", {"fields": ("author_name", "read_time_minutes", "is_featured")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )
