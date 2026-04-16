from modeltranslation.translator import register, TranslationOptions

from .models import SpecialtyArea, SpecialtyCategory


@register(SpecialtyCategory)
class SpecialtyCategoryTR(TranslationOptions):
    fields = ("name",)


@register(SpecialtyArea)
class SpecialtyAreaTR(TranslationOptions):
    fields = (
        "title",
        "short_description",
        "full_description",
        "symptoms",
        "treatment_approach",
        "recovery_info",
        "meta_title",
        "meta_description",
    )
