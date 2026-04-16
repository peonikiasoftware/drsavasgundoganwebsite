from modeltranslation.translator import register, TranslationOptions

from .models import FAQCategory, FAQItem


@register(FAQCategory)
class FAQCategoryTR(TranslationOptions):
    fields = ("name",)


@register(FAQItem)
class FAQItemTR(TranslationOptions):
    fields = ("question", "answer")
