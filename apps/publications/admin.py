from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Publication


@admin.register(Publication)
class PublicationAdmin(TabbedTranslationAdmin):
    list_display = (
        "short_title",
        "journal",
        "year",
        "citation_count",
        "is_featured",
        "order",
    )
    list_filter = ("year", "is_featured", "journal")
    list_editable = ("is_featured", "order")
    search_fields = ("title", "authors", "journal", "doi", "pubmed_id")
    ordering = ("-year", "-citation_count")

    fieldsets = (
        (None, {"fields": ("title", "authors", "journal", "year")}),
        ("Kaynak Detay", {
            "fields": ("volume", "issue", "pages", "doi", "pubmed_id", "pmc_id", "full_url"),
        }),
        ("Özet & Göster", {
            "fields": ("abstract", "citation_count", "is_featured", "order"),
        }),
    )

    @admin.display(description="Başlık", ordering="title")
    def short_title(self, obj):
        return obj.title[:80] + ("…" if len(obj.title) > 80 else "")
