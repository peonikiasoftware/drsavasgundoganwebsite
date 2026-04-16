from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Education, Experience, Membership


@admin.register(Education)
class EducationAdmin(TabbedTranslationAdmin):
    list_display = ("degree", "institution", "year_start", "year_end", "is_highlight", "order")
    list_editable = ("order", "is_highlight")
    list_filter = ("is_highlight",)
    search_fields = ("degree", "institution", "field", "location")
    ordering = ("-year_start", "order")


@admin.register(Experience)
class ExperienceAdmin(TabbedTranslationAdmin):
    list_display = ("position", "institution", "year_start", "year_end", "is_current", "order")
    list_editable = ("order", "is_current")
    list_filter = ("is_current", "is_highlight")
    search_fields = ("position", "institution", "location")
    ordering = ("-year_start", "order")


@admin.register(Membership)
class MembershipAdmin(TabbedTranslationAdmin):
    list_display = ("name", "year_joined", "order")
    list_editable = ("order",)
    search_fields = ("name",)
    ordering = ("order", "name")
