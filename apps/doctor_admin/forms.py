from ckeditor.widgets import CKEditorWidget
from django import forms

from apps.blog.models import BlogPost
from apps.core.models import DoctorProfile, SiteSettings
from apps.experience.models import Education, Experience, Membership
from apps.expertise.models import SpecialtyArea
from apps.faq.models import FAQItem
from apps.media_library.models import Video
from apps.publications.models import Publication


def _input_attrs(extra=None):
    attrs = {"class": "form-input !py-2.5 !border rounded-xl bg-white border-ink-100"}
    if extra:
        attrs.update(extra)
    return attrs


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = (
            "full_name",
            "title_short_tr", "title_short_en",
            "title_long_tr", "title_long_en",
            "hero_headline_tr", "hero_headline_en",
            "hero_subheadline_tr", "hero_subheadline_en",
            "hero_intro_paragraph_tr", "hero_intro_paragraph_en",
            "bio_short_tr", "bio_short_en",
            "bio_long_tr", "bio_long_en",
            "philosophy_quote_tr", "philosophy_quote_en",
            "email_public", "phone_public",
            "appointment_url",
            "hospital_name_tr", "hospital_name_en",
            "hospital_address_tr", "hospital_address_en",
            "google_maps_embed_url",
            "instagram_url", "instagram_handle",
            "linkedin_url", "youtube_url", "facebook_url",
            "google_scholar_url",
            "acibadem_profile_tr", "acibadem_profile_en",
            "portrait_photo", "hero_background", "signature_image",
            "years_of_experience", "publication_count", "procedures_count",
        )
        widgets = {
            "bio_long_tr": CKEditorWidget(config_name="doctor"),
            "bio_long_en": CKEditorWidget(config_name="doctor"),
        }


class BrandingForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = (
            "site_logo", "site_logo_light", "favicon", "default_og_image",
            "social_icon_instagram", "social_icon_scholar",
            "social_icon_linkedin", "social_icon_youtube", "social_icon_facebook",
        )


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = (
            "year_start", "year_end",
            "degree_tr", "degree_en",
            "institution_tr", "institution_en",
            "field_tr", "field_en",
            "location_tr", "location_en",
            "description_tr", "description_en",
            "is_highlight", "order",
        )


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = (
            "year_start", "year_end", "is_current",
            "position_tr", "position_en",
            "institution_tr", "institution_en",
            "location_tr", "location_en",
            "description_tr", "description_en",
            "is_highlight", "order",
        )


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ("name_tr", "name_en", "url", "year_joined", "order")


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = (
            "title_tr", "title_en",
            "authors", "journal", "year",
            "volume", "issue", "pages",
            "doi", "pubmed_id", "pmc_id",
            "citation_count",
            "abstract_tr", "abstract_en",
            "full_url",
            "is_featured", "order",
        )


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = (
            "title_tr", "title_en",
            "description_tr", "description_en",
            "platform", "video_url", "embed_code", "thumbnail",
            "category",
            "is_featured", "is_official_acibadem",
            "publish_date", "order",
        )


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = (
            "title_tr", "title_en",
            "slug", "category", "related_specialty",
            "excerpt_tr", "excerpt_en",
            "content_tr", "content_en",
            "featured_image",
            "read_time_minutes", "status", "published_at",
            "meta_title_tr", "meta_title_en",
            "meta_description_tr", "meta_description_en",
            "is_featured",
        )
        widgets = {
            "content_tr": CKEditorWidget(config_name="doctor"),
            "content_en": CKEditorWidget(config_name="doctor"),
        }


class FAQItemForm(forms.ModelForm):
    class Meta:
        model = FAQItem
        fields = (
            "category",
            "question_tr", "question_en",
            "answer_tr", "answer_en",
            "related_video", "related_specialty",
            "is_featured", "order",
        )


class SpecialtyAreaForm(forms.ModelForm):
    class Meta:
        model = SpecialtyArea
        fields = (
            "category",
            "title_tr", "title_en",
            "slug", "icon", "bento_size",
            "short_description_tr", "short_description_en",
            "full_description_tr", "full_description_en",
            "symptoms_tr", "symptoms_en",
            "treatment_approach_tr", "treatment_approach_en",
            "recovery_info_tr", "recovery_info_en",
            "hero_image",
            "is_featured", "order",
        )
