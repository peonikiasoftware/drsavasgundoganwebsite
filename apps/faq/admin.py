from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import FAQCategory, FAQItem


@admin.register(FAQCategory)
class FAQCategoryAdmin(TabbedTranslationAdmin):
    list_display = ("name", "order")
    list_editable = ("order",)


@admin.register(FAQItem)
class FAQItemAdmin(TabbedTranslationAdmin):
    list_display = ("question", "category", "is_featured", "order")
    list_editable = ("is_featured", "order")
    list_filter = ("category", "is_featured")
    search_fields = ("question", "answer")
    fieldsets = (
        (None, {"fields": ("category", "question", "answer")}),
        ("İlişkili", {"fields": ("related_video", "related_specialty")}),
        ("Görünüm", {"fields": ("is_featured", "order")}),
    )
