from modeltranslation.translator import register, TranslationOptions

from .models import Education, Experience, Membership


@register(Education)
class EducationTR(TranslationOptions):
    fields = ("institution", "degree", "field", "location", "description")


@register(Experience)
class ExperienceTR(TranslationOptions):
    fields = ("position", "institution", "location", "description")


@register(Membership)
class MembershipTR(TranslationOptions):
    fields = ("name",)
