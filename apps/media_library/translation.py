from modeltranslation.translator import register, TranslationOptions

from .models import Video, VideoCategory


@register(VideoCategory)
class VideoCategoryTR(TranslationOptions):
    fields = ("name",)


@register(Video)
class VideoTR(TranslationOptions):
    fields = ("title", "description")
