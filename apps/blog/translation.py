from modeltranslation.translator import register, TranslationOptions

from .models import BlogCategory, BlogPost


@register(BlogCategory)
class BlogCategoryTR(TranslationOptions):
    fields = ("name", "description")


@register(BlogPost)
class BlogPostTR(TranslationOptions):
    fields = ("title", "excerpt", "content", "meta_title", "meta_description")
