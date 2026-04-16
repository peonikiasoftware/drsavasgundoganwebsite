from modeltranslation.translator import register, TranslationOptions

from .models import Publication


@register(Publication)
class PublicationTR(TranslationOptions):
    fields = ("title", "abstract")
