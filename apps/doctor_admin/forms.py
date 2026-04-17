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


# Shared help text for the "Sıra" (order) field — applied via __init__
ORDER_HELP_TEXT = (
    "Sıralama numarası. Küçük numaralar önce gösterilir "
    "(örn. 0 en önde, 10 sonra gelir). Aynı numaraya sahip kayıtlar "
    "kendi içinde tarihe veya başlığa göre sıralanır. 10'ar 10'ar "
    "artırarak (0, 10, 20...) daha sonra araya ekleme yapmak kolaylaşır."
)


def _apply_order_help(form):
    """Attach the shared help text to the 'order' field if present."""
    if "order" in form.fields:
        form.fields["order"].help_text = ORDER_HELP_TEXT


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
        help_texts = {"order": ORDER_HELP_TEXT}


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
        help_texts = {"order": ORDER_HELP_TEXT}


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ("name_tr", "name_en", "url", "year_joined", "order")
        help_texts = {"order": ORDER_HELP_TEXT}


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
        help_texts = {"order": ORDER_HELP_TEXT}


class VideoForm(forms.ModelForm):
    """Video form — adds an optional 'new category' field so the doctor can
    create a new VideoCategory inline without leaving the page."""

    new_category = forms.CharField(
        label="Yeni Kategori (opsiyonel)",
        required=False,
        max_length=120,
        help_text=(
            "Yukarıdaki listede uygun kategori yoksa yeni kategori adını buraya "
            "yazın — kaydedilince otomatik oluşturulur ve bu videoya atanır."
        ),
    )

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
        help_texts = {
            "order": ORDER_HELP_TEXT,
            "title_tr": "Zorunlu alan. Video için Türkçe başlık.",
            "video_url": "Zorunlu alan. Instagram Reel veya YouTube video bağlantısının tamamı (örn. https://www.instagram.com/reel/XXXX/).",
            "platform": "Videonun kaynağı — Instagram, YouTube veya Acıbadem resmi.",
            "embed_code": "İsteğe bağlı. Platform iframe'i otomatik oluşturulamıyorsa özel HTML buraya yapıştırılabilir.",
            "category": "Mevcut kategoriyi seçin veya aşağıdaki 'Yeni Kategori' alanını doldurun.",
            "thumbnail": "İsteğe bağlı. Boş bırakılırsa YouTube videoları için otomatik kapak kullanılır, Instagram için ilk kare gösterilir.",
            "is_featured": "İşaretlenirse ana sayfa video bölümünde ve liste başında öne çıkar.",
            "is_official_acibadem": "Bu video Acıbadem resmi hesabında yayınlandıysa işaretleyin (ekstra rozet alır).",
            "publish_date": "Videonun yayınlandığı tarih (opsiyonel — liste sıralamasını etkiler).",
        }

    def save(self, commit=True):
        from django.utils.text import slugify
        from apps.media_library.models import VideoCategory

        new_name = (self.cleaned_data.get("new_category") or "").strip()
        if new_name:
            base_slug = slugify(new_name) or "kategori"
            slug = base_slug
            i = 2
            while VideoCategory.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            cat = VideoCategory.objects.create(name=new_name, slug=slug)
            self.instance.category = cat
        return super().save(commit=commit)


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
        help_texts = {
            "title_tr": "Zorunlu alan. Yazının Türkçe başlığı.",
            "slug": "URL dostu kısa ad (küçük harf, tire ile ayrılmış). Boş bırakılırsa başlıktan otomatik üretilir.",
            "excerpt_tr": "Blog liste kartında görünecek 2-3 cümlelik özet (Türkçe).",
            "status": "'Taslak' siteye çıkmaz, 'Yayında' siteye çıkar, 'Arşiv' gizlenir.",
            "published_at": "Yayın tarihi. Boş bırakılırsa 'Yayında' seçildiğinde otomatik o an atanır.",
            "read_time_minutes": "Okuyucuya gösterilecek yaklaşık okuma süresi (dakika).",
            "is_featured": "İşaretlenirse ana sayfadaki blog bölümünde öne çıkar.",
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
        help_texts = {"order": ORDER_HELP_TEXT}


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
        help_texts = {"order": ORDER_HELP_TEXT}
