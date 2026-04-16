from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import SpecialtyArea, SpecialtyCategory


@admin.register(SpecialtyCategory)
class SpecialtyCategoryAdmin(TabbedTranslationAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(SpecialtyArea)
class SpecialtyAreaAdmin(TabbedTranslationAdmin):
    list_display = ("title", "category", "is_featured", "bento_size", "order")
    list_editable = ("order", "is_featured", "bento_size")
    list_filter = ("category", "is_featured")
    search_fields = ("title", "short_description")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "icon")}),
        ("Ana Sayfa / Kart", {
            "fields": ("short_description", "hero_image", "is_featured", "bento_size", "order"),
        }),
        ("Detay İçerik", {
            "fields": ("full_description", "symptoms", "treatment_approach", "recovery_info"),
        }),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )
