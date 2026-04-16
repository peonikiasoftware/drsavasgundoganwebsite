from modeltranslation.translator import register, TranslationOptions

from .models import DoctorProfile, SiteSettings


@register(DoctorProfile)
class DoctorProfileTR(TranslationOptions):
    fields = (
        "title_short",
        "title_long",
        "hero_headline",
        "hero_subheadline",
        "hero_intro_paragraph",
        "bio_short",
        "bio_long",
        "philosophy_quote",
        "hospital_name",
        "hospital_address",
    )


@register(SiteSettings)
class SiteSettingsTR(TranslationOptions):
    fields = (
        "default_meta_title",
        "default_meta_description",
        "cookie_banner_text",
        "kvkk_body",
        "privacy_body",
    )
