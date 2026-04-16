# CLAUDE.md — Op. Dr. Savaş Gündoğan Resmi Web Sitesi

> **Bu dosya Claude Code için bir yapılacaklar ve kurallar manifestosudur.**
> Projenin kök dizinine `CLAUDE.md` olarak konmuştur ve Claude Code otomatik olarak okur.
> Her komut çalıştırmadan önce bu dosyayı referans al. Karar verirken bu dosyaya sadık kal.
> Bu dosyadaki talimatlar ile kullanıcı mesajı çelişirse, **kullanıcı mesajı önceliklidir** — ancak güvenlik kuralları (bkz. §12) asla ezilemez.

---

## 0. HIZLI REFERANS (TL;DR)

| Alan | Karar |
|---|---|
| **Framework** | Django 5.2 LTS (Python 3.12) |
| **Frontend** | Django Templates + Tailwind CSS (CDN değil, build edilmiş) + Alpine.js + HTMX |
| **DB (dev)** | SQLite (`db.sqlite3`, `.gitignore` içinde) |
| **DB (prod)** | Supabase PostgreSQL (Vercel ile uyumlu, `psycopg2-binary`) |
| **Media Storage** | Cloudinary (Vercel serverless ephemeral FS sorununu çözer) |
| **Static Files** | WhiteNoise + `collectstatic` |
| **Admin Teması** | `django-jazzmin` |
| **Çeviri** | `django-modeltranslation` (TR varsayılan, EN toggle) |
| **Env Yönetimi** | `django-environ` + `.env` (asla commit edilmez) |
| **Deployment** | Vercel (GitHub push → otomatik deploy) |
| **Ana Renk** | Teal `#00A0B0` / Accent `#007B8A` / BG `#F8F9FA` / Text `#1A1A1A` |
| **Font** | Inter (body) + Fraunces veya Playfair Display (headings, "tıbbi lüks" hissi için) |
| **Paket yöneticisi** | `pip` + `requirements.txt` (production'da `requirements.txt`; dev'de `requirements-dev.txt`) |

### ÇOK ÖNEMLİ KISITLAMALAR — İLK OKUDUĞUNDA İÇSELLEŞTİR
1. **Hasta yorumu/testimonial bölümü YAPMA.** Hocada şu an gerçek hasta yorumu yok. Bu bölümü eklemezsen "yorum yok" boşluğu da olmaz. İçeriği olmayan bölüm hiç koyulmasın.
2. **Vercel serverless = yazılabilir dosya sistemi YOK.** Bu yüzden:
   - SQLite prod'da ÇALIŞMAZ → Supabase Postgres.
   - `MEDIA_ROOT` dosya yolu ÇALIŞMAZ → Cloudinary.
   - `collectstatic` build sırasında WhiteNoise ile halledilir.
3. **GitHub'a push edilecek kod:** Hiçbir `.env`, hiçbir hard-coded secret, hiçbir gerçek şifre, hiçbir database URL olmayacak. Tümü Vercel Environment Variables'tan okunur.
4. **"AI üretimi gibi" durmayacak tasarım:** Generic bootstrap kartları, her yerde aynı mavi, sıkıcı typography, stock hero görseli YOK. Bkz. §7 "Tasarım Anti-Patterns".

---

## 1. PROJE BAĞLAMI

### 1.1 Hoca Hakkında (Doğrulanmış, Nisan 2026)
- **Ad:** Op. Dr. Savaş Gündoğan (M.D. Savaş Gündoğan)
- **Uzmanlık:** Kadın Hastalıkları ve Doğum (Jinekoloji & Obstetrik)
- **Kurum:** Acıbadem Maslak Hastanesi
- **Adres:** Büyükdere Cad. No:40, 34457 Maslak / İstanbul
- **Resmi E-posta (site'de görünür):** `savas.gundogan@acibadem.com`
- **Acıbadem Profil URL'leri:**
  - TR: `https://www.acibadem.com.tr/doktor/savas-gundogan/`
  - EN: `https://www.acibadem.com.tr/en/doctor/savas-gundogan/`
  - Int'l: `https://acibademinternational.com/doctor/savas-gundogan/`
- **Google Scholar:** `https://scholar.google.com/citations?user=9hUh--8AAAAJ&hl=en`
- **Instagram:** `https://www.instagram.com/dr.savasgundogan/` (@dr.savasgundogan)
- **Randevu linki:** Acıbadem web sayfasındaki "Randevu Al" butonu — `https://www.acibadem.com.tr/doktor/savas-gundogan/` sayfasındaki randevu formu.

### 1.2 Kullanıcı Profilleri (Site Yöneticileri)
1. **Murat Emre** (kullanıcı / superuser) — full-stack access, teknik yönetim.
2. **Op. Dr. Savaş Gündoğan** (doktor / staff user) — sadece kendi içerik alanı; basit, Türkçe, büyük-buton arayüzü.

Her iki kullanıcının parolası **yalnızca** `.env` ve Vercel Env Variables içinde tutulur. Initial data fixture'ları varsa bile parolalar oraya yazılmaz — `createsuperuser` komutu deploy sonrası manuel veya management command ile atılır.

### 1.3 Tone & Mission
Site, "lüks butik klinik" hissi verecek. Minimal invaziv cerrahide uzmanlaşmış, uluslararası deneyimli (İtalya — Università degli Studi dell'Insubria), 20+ uluslararası yayına sahip bir cerrahın dijital vitrini. Hedef kitle: 28-55 yaş, bilgili, seçici kadın hastalar + hekim arkadaşlar + akademisyenler.

---

## 2. TEKNİK STACK — KESİN KARARLAR

### 2.1 Versiyonlar (requirements.txt için baz alınacak)
```
Django==5.2.*           # LTS, Python 3.12 destekli, 3 yıl güvenlik desteği
psycopg2-binary==2.9.*  # Supabase Postgres için (binary şart — Vercel build'inde pg_config yok)
django-environ==0.12.*
whitenoise==6.8.*
django-modeltranslation==0.19.*
django-jazzmin==3.0.*
cloudinary==1.41.*
django-cloudinary-storage==0.3.*
Pillow==11.*
gunicorn==23.*          # Lokal prod-like test için (Vercel WSGI kendi yönetir)
django-htmx==1.19.*
django-widget-tweaks==1.5.*  # Form field class override için
django-ckeditor==6.7.*  # Blog & bio zengin metin editörü için (veya tinymce)
requests==2.32.*
python-slugify==8.0.*
```
Dev-only (`requirements-dev.txt`):
```
django-debug-toolbar==4.4.*
black==24.*
ruff==0.6.*
```

### 2.2 Neden Bu Seçimler?
- **Django 5.2 LTS:** Güvenlik güncellemeleri Nisan 2028'e kadar. Python 3.12 stable.
- **Tailwind CSS (CDN değil, build edilmiş):** Prod'da CDN yavaş + unused CSS'yi tree-shake etmek şart. `django-tailwind` paketi yerine **manuel kurulum** önerilir çünkü Vercel build süresini kısaltır. Alternatif: CDN'i sadece dev'de, prod'da `output.css` (build edilmiş, minified) kullan.
- **Alpine.js:** Hafif interaktivite (dropdown, mobile menu, modal). jQuery kullanma.
- **HTMX:** Form submission, infinite scroll, dil değiştirme gibi SPA hissi için. React KULLANMA — overkill.
- **Cloudinary:** Vercel serverless'ta `MEDIA_ROOT` yok. Cloudinary free tier 25GB storage + 25GB bandwidth / ay. Otomatik WebP dönüşümü, lazy transform. Cloudflare R2 + django-storages alternatif olabilir ama Cloudinary zero-config.
- **Supabase Postgres:** Free tier 500MB — bu site için fazlasıyla yeter. Vercel Marketplace üzerinden Neon da olur; ikisi de iş görür. **Karar: Supabase** (Storage ihtiyacı olursa ileride aynı yerde).
- **django-jazzmin:** Admin paneline modern görünüm, dark mode, sidebar. Doktor için friendly UI bu temanın üzerine kurulacak.

---

## 3. DİZİN YAPISI — BÖYLE OLUŞTUR

```
drsavasgundogan-v1/
├── .venv/                          # Zaten var (e:/WEBSITES/drsavasgundogan-v1/.venv)
├── .env                            # GIT IGNORE — asla commit etme
├── .env.example                    # Örnek, boş değerlerle — commit edilir
├── .gitignore                      # Aşağıda içeriği var
├── .python-version                 # "3.12" yaz
├── CLAUDE.md                       # Bu dosya
├── README.md                       # Kurulum + deploy talimatları
├── ADMIN_PANEL_DOC.md              # Admin kullanım kılavuzu (hoca için)
├── requirements.txt
├── requirements-dev.txt
├── vercel.json                     # Vercel config
├── build_files.sh                  # Vercel build script (migrate + collectstatic)
├── manage.py
│
├── config/                         # Django project (settings paketi)
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py                     # Vercel entry point
│   ├── urls.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py                 # Ortak ayarlar
│       ├── dev.py                  # DEBUG=True, SQLite
│       └── prod.py                 # DEBUG=False, Postgres, Cloudinary, WhiteNoise
│
├── apps/
│   ├── __init__.py
│   ├── core/                       # DoctorProfile, SiteSettings, Contact form
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── translation.py          # modeltranslation kayıtları
│   │   ├── context_processors.py   # global template context
│   │   └── migrations/
│   ├── experience/                 # Education, Experience, Memberships
│   ├── publications/               # Academic publications
│   ├── expertise/                  # Specialty areas
│   ├── media_library/              # Videos (Instagram Reels, YouTube)
│   ├── blog/                       # Blog posts
│   ├── faq/                        # FAQ
│   └── doctor_admin/               # Dr. Savaş için özel dashboard
│       ├── views.py
│       ├── urls.py
│       ├── templates/doctor_admin/
│       └── decorators.py           # @doctor_required
│
├── templates/
│   ├── base.html                   # Header + footer + meta
│   ├── partials/
│   │   ├── _header.html
│   │   ├── _footer.html
│   │   ├── _mobile_menu.html
│   │   ├── _language_toggle.html
│   │   ├── _floating_appointment.html
│   │   ├── _cookie_banner.html
│   │   └── _seo_meta.html
│   ├── core/
│   │   ├── home.html
│   │   ├── about.html
│   │   ├── contact.html
│   │   └── privacy.html
│   ├── expertise/
│   │   ├── list.html
│   │   └── detail.html
│   ├── experience/
│   │   └── timeline.html
│   ├── publications/
│   │   └── list.html
│   ├── media_library/
│   │   └── list.html
│   ├── blog/
│   │   ├── list.html
│   │   └── detail.html
│   ├── faq/
│   │   └── list.html
│   └── doctor_admin/
│       ├── dashboard.html
│       └── ...
│
├── static/                         # Kaynak (src) static dosyalar
│   ├── src/
│   │   ├── css/
│   │   │   └── input.css           # Tailwind giriş
│   │   ├── js/
│   │   │   ├── alpine-components.js
│   │   │   └── htmx-config.js
│   │   └── fonts/                  # self-hosted Inter + Fraunces
│   ├── dist/                       # Build çıktısı (collectstatic öncesi)
│   │   └── css/output.css
│   └── images/
│       └── placeholders/
│
├── staticfiles/                    # collectstatic çıktısı (GIT IGNORE)
├── locale/                         # translation .po dosyaları
│   ├── tr/LC_MESSAGES/
│   └── en/LC_MESSAGES/
│
├── package.json                    # Tailwind build için
├── package-lock.json
├── tailwind.config.js
└── postcss.config.js
```

### 3.1 `.gitignore` (EN AZ bunları içer)
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
env/

# Django
*.log
db.sqlite3
db.sqlite3-journal
staticfiles/
media/
/static/dist/

# Env
.env
.env.*
!.env.example

# Node
node_modules/
npm-debug.log
yarn-error.log

# IDE
.vscode/
.idea/
*.swp
.DS_Store

# Vercel
.vercel

# Tests / Coverage
.coverage
htmlcov/
.pytest_cache/

# Translations (derlenmişler commit edilmez, .po edilir)
*.mo
```

### 3.2 `.env.example` (Commit edilecek, şablon)
```env
# Django
DJANGO_SECRET_KEY=change-me-generate-with-get_random_secret_key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.dev

# Database (prod için Supabase)
DATABASE_URL=postgresql://user:password@host:5432/dbname
# veya
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=5432

# Cloudinary
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# Admin seed (sadece ilk kurulum için, sonra silinebilir)
ADMIN_SUPERUSER_USERNAME=murat_admin
ADMIN_SUPERUSER_EMAIL=
ADMIN_SUPERUSER_PASSWORD=

DOCTOR_ADMIN_USERNAME=dr_savas
DOCTOR_ADMIN_EMAIL=
DOCTOR_ADMIN_PASSWORD=

# Analytics (opsiyonel)
GOOGLE_ANALYTICS_ID=
```

---

## 4. DATABASE MODELLERİ — DETAYLI

**Tüm metin alanları çok dilli (`django-modeltranslation`)**. Aşağıdaki tabloda `TR/EN` işareti olan alanlar çevrilebilir.

### 4.1 `apps/core/models.py`

#### `DoctorProfile` (Singleton — sadece 1 kayıt)
```python
class DoctorProfile(models.Model):
    # Temel
    full_name = CharField                   # "Op. Dr. Savaş Gündoğan"
    title_short = CharField                 # "Op. Dr." (TR/EN)
    title_long = CharField                  # "Kadın Hastalıkları ve Doğum Uzmanı" (TR/EN)
    hero_headline = CharField               # Ana sayfa ana başlık (TR/EN)
    hero_subheadline = TextField            # Ana sayfa alt başlık (TR/EN)
    hero_intro_paragraph = TextField        # (TR/EN)

    # Fotoğraflar (Cloudinary)
    portrait_photo = CloudinaryField        # Profesyonel portre
    hero_background = CloudinaryField       # Hero arka plan
    signature_image = CloudinaryField       # Opsiyonel, imza

    # Biyografi
    bio_short = TextField                   # 150 kelime (TR/EN)
    bio_long = RichTextField                # Uzun özgeçmiş (TR/EN)
    philosophy_quote = TextField            # "Neden jinekoloji?" alıntısı (TR/EN)

    # İletişim
    email_public = EmailField               # savas.gundogan@acibadem.com
    phone_public = CharField                # Opsiyonel
    appointment_url = URLField              # Acıbadem randevu URL'i
    hospital_name = CharField               # "Acıbadem Maslak Hastanesi"
    hospital_address = TextField            # Tam adres
    google_maps_embed_url = TextField       # iframe src

    # Sosyal medya
    instagram_url = URLField
    instagram_handle = CharField            # "@dr.savasgundogan"
    linkedin_url = URLField(blank=True)
    youtube_url = URLField(blank=True)
    facebook_url = URLField(blank=True)
    google_scholar_url = URLField

    # Sayaçlar (manuel girilebilir, opsiyonel)
    years_of_experience = IntegerField      # 12
    publication_count = IntegerField        # 20
    procedures_count = IntegerField(blank=True, null=True)

    updated_at = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Doktor Profili"
        verbose_name_plural = "Doktor Profili"

    def save(self, *args, **kwargs):
        # Singleton zorlama
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
```

#### `SiteSettings` (Singleton)
```python
class SiteSettings(models.Model):
    site_name = CharField                   # "Op. Dr. Savaş Gündoğan"
    default_meta_title = CharField          # SEO varsayılan (TR/EN)
    default_meta_description = TextField    # (TR/EN)
    default_og_image = CloudinaryField
    cookie_banner_text = TextField          # KVKK metni (TR/EN)
    newsletter_enabled = BooleanField(default=False)
    google_analytics_id = CharField(blank=True)
    maintenance_mode = BooleanField(default=False)
```

#### `ContactMessage`
```python
class ContactMessage(models.Model):
    name = CharField
    email = EmailField
    phone = CharField(blank=True)
    subject = CharField(blank=True)
    message = TextField
    is_read = BooleanField(default=False)
    is_archived = BooleanField(default=False)
    kvkk_consent = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    ip_address = GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
```

### 4.2 `apps/experience/models.py`

```python
class Education(models.Model):
    institution = CharField                 # (TR/EN)
    degree = CharField                      # (TR/EN) "Tıp Doktoru", "Uzmanlık"
    field = CharField(blank=True)           # (TR/EN)
    location = CharField                    # "İstanbul, Türkiye" (TR/EN)
    year_start = IntegerField
    year_end = IntegerField(null=True, blank=True)  # null = devam ediyor
    description = TextField(blank=True)     # (TR/EN)
    order = PositiveIntegerField(default=0) # Sıralama
    is_highlight = BooleanField(default=False)  # Ana sayfa highlight için

    class Meta:
        ordering = ['-year_start', 'order']


class Experience(models.Model):
    position = CharField                    # (TR/EN) "Uzman Hekim", "Asistan Hekim"
    institution = CharField                 # (TR/EN)
    location = CharField                    # (TR/EN)
    year_start = IntegerField
    year_end = IntegerField(null=True, blank=True)
    is_current = BooleanField(default=False)
    description = TextField(blank=True)     # (TR/EN)
    order = PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-year_start', 'order']


class Membership(models.Model):
    name = CharField                        # (TR/EN) Dernek adı
    url = URLField(blank=True)
    year_joined = IntegerField(blank=True, null=True)
    order = PositiveIntegerField(default=0)
```

### 4.3 `apps/expertise/models.py`

```python
class SpecialtyCategory(models.Model):
    name = CharField                        # (TR/EN) "Minimal İnvaziv Cerrahi"
    slug = SlugField(unique=True)
    icon = CharField(blank=True)            # Lucide icon name veya SVG
    order = PositiveIntegerField(default=0)


class SpecialtyArea(models.Model):
    category = ForeignKey(SpecialtyCategory, null=True, blank=True)
    title = CharField                       # (TR/EN) "Endometriozis Tedavisi"
    slug = SlugField(unique=True)
    icon = CharField                        # Lucide: 'heart-pulse', 'stethoscope' vb.
    short_description = CharField(max_length=240)  # (TR/EN) 2 cümle
    full_description = RichTextField        # (TR/EN) Detay sayfası için
    symptoms = RichTextField(blank=True)    # (TR/EN) "Belirtileri"
    treatment_approach = RichTextField(blank=True)  # (TR/EN) "Tedavi yaklaşımım"
    recovery_info = RichTextField(blank=True)       # (TR/EN) "İyileşme süreci"
    hero_image = CloudinaryField(blank=True, null=True)
    order = PositiveIntegerField(default=0)
    is_featured = BooleanField(default=False)  # Ana sayfa öne çıkan
    meta_title = CharField(blank=True)      # (TR/EN)
    meta_description = TextField(blank=True) # (TR/EN)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']
```

### 4.4 `apps/publications/models.py`

```python
class Publication(models.Model):
    title = TextField                       # (TR/EN) Makale başlığı
    authors = CharField                     # "Takmaz O, Bastu E, Ozbasli E, Gundogan S..."
    journal = CharField                     # "J Minim Invasive Gynecol"
    year = PositiveIntegerField
    volume = CharField(blank=True)
    issue = CharField(blank=True)
    pages = CharField(blank=True)
    doi = CharField(blank=True)
    pubmed_id = CharField(blank=True)
    pmc_id = CharField(blank=True)
    citation_count = PositiveIntegerField(default=0)
    abstract = TextField(blank=True)        # (TR/EN) Özet — pop-up için
    full_url = URLField(blank=True)         # Orijinal link
    is_featured = BooleanField(default=False)
    order = PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-year', '-citation_count']
```

### 4.5 `apps/media_library/models.py`

```python
class VideoCategory(models.Model):
    name = CharField                        # (TR/EN) "Menopoz", "Endometriozis"
    slug = SlugField(unique=True)
    order = PositiveIntegerField(default=0)


class Video(models.Model):
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram Reel'),
        ('youtube', 'YouTube'),
        ('youtube_short', 'YouTube Short'),
        ('acibadem', 'Acıbadem Resmi'),
    ]

    title = CharField                       # (TR/EN)
    description = TextField                 # (TR/EN)
    platform = CharField(choices=PLATFORM_CHOICES)
    video_url = URLField                    # Instagram reel URL veya YouTube
    embed_code = TextField(blank=True)      # Gerekirse custom embed
    thumbnail = CloudinaryField(blank=True, null=True)  # Otomatik alınamazsa manuel
    category = ForeignKey(VideoCategory, null=True, blank=True)
    is_featured = BooleanField(default=False)
    is_official_acibadem = BooleanField(default=False)  # Hero'da özel badge
    publish_date = DateField(blank=True, null=True)
    order = PositiveIntegerField(default=0)
    view_count_manual = PositiveIntegerField(default=0, blank=True)  # Opsiyonel

    class Meta:
        ordering = ['-is_featured', 'order', '-publish_date']
```

**Not:** Instagram reel embed için `https://www.instagram.com/reel/{REEL_ID}/embed` URL'i iframe ile kullanılır. Otomatik thumbnail çekmek için Instagram Graph API gerekir (kompleks) — bu projede thumbnail manuel yüklenir.

### 4.6 `apps/blog/models.py`

```python
class BlogCategory(models.Model):
    name = CharField                        # (TR/EN)
    slug = SlugField(unique=True)
    description = TextField(blank=True)     # (TR/EN)
    order = PositiveIntegerField(default=0)


class BlogPost(models.Model):
    STATUS_CHOICES = [('draft', 'Taslak'), ('published', 'Yayında'), ('archived', 'Arşiv')]

    title = CharField                       # (TR/EN)
    slug = SlugField(unique=True)
    category = ForeignKey(BlogCategory, null=True, blank=True)
    related_specialty = ForeignKey('expertise.SpecialtyArea', null=True, blank=True)
    excerpt = TextField(max_length=320)     # (TR/EN) Liste için özet
    content = RichTextField                 # (TR/EN) Ana içerik
    featured_image = CloudinaryField(blank=True, null=True)
    author_name = CharField(default="Op. Dr. Savaş Gündoğan")
    read_time_minutes = PositiveIntegerField(default=5)
    status = CharField(choices=STATUS_CHOICES, default='draft')
    published_at = DateTimeField(null=True, blank=True)
    meta_title = CharField(blank=True)
    meta_description = TextField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    view_count = PositiveIntegerField(default=0)
    is_featured = BooleanField(default=False)

    class Meta:
        ordering = ['-published_at', '-created_at']
```

### 4.7 `apps/faq/models.py`

```python
class FAQCategory(models.Model):
    name = CharField                        # (TR/EN)
    order = PositiveIntegerField(default=0)


class FAQItem(models.Model):
    category = ForeignKey(FAQCategory, null=True, blank=True)
    question = CharField                    # (TR/EN)
    answer = RichTextField                  # (TR/EN)
    related_video = ForeignKey('media_library.Video', null=True, blank=True)
    related_specialty = ForeignKey('expertise.SpecialtyArea', null=True, blank=True)
    order = PositiveIntegerField(default=0)
    is_featured = BooleanField(default=False)

    class Meta:
        ordering = ['order', 'id']
```

### 4.8 Translation Setup
Her app için `translation.py` oluştur. Örnek:

```python
# apps/expertise/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import SpecialtyArea, SpecialtyCategory

@register(SpecialtyCategory)
class SpecialtyCategoryTR(TranslationOptions):
    fields = ('name',)

@register(SpecialtyArea)
class SpecialtyAreaTR(TranslationOptions):
    fields = ('title', 'short_description', 'full_description',
              'symptoms', 'treatment_approach', 'recovery_info',
              'meta_title', 'meta_description')
```

---

## 5. SAYFA SAYFA İÇERİK HARİTASI

> **Her sayfa için aşağıdaki şablonu uygula:** Sayfanın URL'i, Django view adı, template yolu, hangi model(ler)den veri çeker, hangi bölümlere sahip, hangi içeriği gösterir.
> **Lorem ipsum YOK.** Eğer bir içerik yoksa, o bölümü fiziksel olarak oluşturma.

### 5.1 URL Yapısı
```python
# config/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),  # set_language view
    path('doctor-admin/', include('apps.doctor_admin.urls')),
]

urlpatterns += i18n_patterns(
    path('', include('apps.core.urls')),                  # /, /hakkimda, /iletisim
    path('uzmanlik/', include('apps.expertise.urls')),    # /uzmanlik/, /uzmanlik/endometriozis
    path('kariyer/', include('apps.experience.urls')),    # /kariyer/
    path('yayinlar/', include('apps.publications.urls')), # /yayinlar/
    path('videolar/', include('apps.media_library.urls')), # /videolar/
    path('blog/', include('apps.blog.urls')),             # /blog/, /blog/slug
    path('sss/', include('apps.faq.urls')),               # /sss/
    prefix_default_language=True,  # /tr/ ve /en/ prefix zorunlu
)
```

Django `i18n_patterns` ile her URL `/tr/...` veya `/en/...` olur. Kullanıcı dili değiştirdiğinde HTMX ile set_language post eder, sayfa yenilenir.

### 5.2 Sayfa: **Ana Sayfa** (`/`)

- **View:** `apps.core.views.HomeView`
- **Template:** `templates/core/home.html`
- **Hangi modeller:** `DoctorProfile.load()`, `SpecialtyArea.objects.filter(is_featured=True)[:6]`, `Video.objects.filter(is_featured=True)[:3]`, `BlogPost.objects.filter(status='published', is_featured=True)[:3]`, `Publication.objects.filter(is_featured=True)[:3]`

#### Bölümler (yukarıdan aşağıya):

**1) Hero Section (viewport-height 90vh)**
- **Arka plan:** `DoctorProfile.hero_background` (dark overlay %40)
- **Sol 60% (desktop):**
  - Küçük eyebrow etiketi (teal renkli): "Acıbadem Maslak Hastanesi"
  - H1: `DoctorProfile.hero_headline` — "Minimal İnvaziv Jinekolojik Cerrahi ve Kadın Sağlığı" (Fraunces font, 56px desktop, italic accent kelimeler)
  - Alt başlık (serif, ışıl): `DoctorProfile.hero_subheadline` — "Laparoskopi • Robotik Cerrahi • vNOTES • Endometriozis • Ürojinekoloji"
  - Paragraf: `DoctorProfile.hero_intro_paragraph`
  - 3 rozet satırı: "12+ Yıl Deneyim" · "İtalya Eğitimli" · "20+ Uluslararası Yayın"
  - 2 CTA buton: birincil teal "Randevu Al" (Acıbadem linkine), ikincil outline "Videolarımı İzle" (/#videolar)
- **Sağ 40% (desktop) veya tam genişlik altta (mobil):**
  - Büyük Instagram Reel embed (özel kart içinde): `https://www.instagram.com/reel/DUs9VxiDBej/embed`
  - Üst sticker: "ACIBADEM RESMİ HESABINDA YAYINLANDI" (gold rozet)
  - Alt yazı: "Kişiye Özel Hormon Tedavisi"
  - Aşağıda: "Vajinal kuruluk, menopoz ve idrar kaçırma sorunlarına modern yaklaşım"

**2) Güven Bandı (Trust Strip)**
İnce teal çizgi arası 4 istatistik (sayaç animasyonu Alpine.js ile):
- 12+ Yıl Klinik Deneyim
- 20+ Uluslararası Yayın
- İtalya Minimal İnvaziv Eğitimi (Università degli Studi dell'Insubria)
- Acıbadem Sağlık Grubu Uzman Hekimi

**3) "Uzmanlık Alanlarım" Öne Çıkanlar (6 kart grid)**
- Başlık: "Uzmanlık Alanlarım" / "Areas of Expertise"
- Üst kicker: "Özenle • Bilimle • Modern Tekniklerle"
- 6 kart — `SpecialtyArea.is_featured=True` olanlardan:
  - Her kart: Lucide icon (circle teal bg), title, short_description, "Detay →" link
  - Hover: hafif yukarı kayar + gölge derinleşir
- Alt: "Tüm Uzmanlık Alanlarım" büyük teal outline buton → `/uzmanlik/`

**4) "Neden Beni Tercih Etmelisiniz?" (3 kolonlu özellik)**
*Hardcode edilmiş içerik (SiteSettings ile opsiyonel dinamikleştirilebilir):*
- **Uluslararası Deneyim** — İtalya'da Università degli Studi dell'Insubria'da minimal invaziv cerrahi eğitimi aldım. Dünya standartlarında teknikleri kliniğime taşıyorum.
- **Minimal İnvaziv Uzmanlığı** — vNOTES (izsiz vajinal cerrahi), robotik cerrahi ve tek-port laparoskopi ile daha kısa iyileşme, minimum iz.
- **Hasta Odaklı Yaklaşım** — Her hasta özeldir. Tedavi planı, yaşam tarzına ve beklentilerine göre birebir tasarlanır.

**5) Akademik Kimlik (compact)**
- Başlık: "Akademik Araştırmalarım"
- Kısa metin: "Minimal invaziv cerrahi, robotik myomektomi ve endometriozis üzerine Journal of Minimally Invasive Gynecology başta olmak üzere prestijli dergilerde 20+ uluslararası yayın."
- 3 öne çıkan yayın kartı (`Publication.is_featured=True`)
- Link: "Tüm Yayınlarım →" + "Google Scholar Profilim →" (link: scholar URL)

**6) "Son Videolar" (3-5 kart)**
- `Video.is_featured=True` olanlar
- Thumbnail + başlık + "İzle" butonu
- Modal ile aç (Alpine.js)
- Alt link: "Tüm Videolar →"

**7) "Blog'dan Son Yazılar" (3 kart — VARSA)**
- `BlogPost.status='published'` son 3
- **Eğer hiç blog yazısı yoksa bu section gizli** (template'de `{% if posts %}` koy).

**8) Kısa Biyografi Bandı**
- Sol: `DoctorProfile.portrait_photo` (yuvarlak, gold border)
- Sağ: `DoctorProfile.bio_short` + "Hakkımda daha fazla →" link

**9) İletişim / Randevu CTA (full width band)**
- Teal gradient arkaplan
- Başlık: "Sağlığınız için bir adım atın"
- Metin: "Randevu talebiniz veya sorunuz için bize ulaşın."
- 2 buton: "Randevu Al" (Acıbadem link) + "Mesaj Gönder" (/iletisim)

### 5.3 Sayfa: **Hakkımda** (`/hakkimda/`)

- **View:** `AboutView`
- **Modeller:** `DoctorProfile`, `Education`, `Experience`, `Membership`

**Bölümler:**
1. **Hero (smaller, 60vh):** Büyük portre fotoğraf solda, sağda ad + titles + kısa bio + sosyal medya ikonları
2. **"Hikayem" / "My Story":** `DoctorProfile.bio_long` (RichText)
3. **Felsefem:** `philosophy_quote` — italic, büyük, tırnak içinde
4. **Eğitim Timeline:** `Education` dikey timeline, yıl vurgulu
5. **Deneyim Timeline:** `Experience` benzer şekilde
6. **Üyelikler:** `Membership` liste halinde (ufak logolar)
7. **Alt CTA:** Randevu + Instagram profile link

### 5.4 Sayfa: **Uzmanlık Alanlarım** (`/uzmanlik/`)

- **Liste sayfası:** Tüm `SpecialtyArea` kategoriye göre gruplu
- **Detay sayfası** (`/uzmanlik/<slug>/`):
  - Hero image + başlık
  - Kısa tanım (mavi kutu içinde)
  - Bölümler: "Belirtiler" / "Tedavi Yaklaşımım" / "İyileşme Süreci"
  - İlgili videolar (varsa `Video.objects.filter(...)` basit bağlantı)
  - İlgili blog yazıları (varsa)
  - SSS'den ilgili sorular
  - CTA: Randevu + iletişim formu

**Karar:** Detay sayfası sadece `is_featured` veya veri zengin olanlar için gösterilir; yoksa direkt liste sayfasında kart açılır.

### 5.5 Sayfa: **Eğitim & Deneyim** (`/kariyer/`)

Sol kolon `Education`, sağ kolon `Experience` timeline. Alt: `Membership` liste.

### 5.6 Sayfa: **Akademik Yayınlar** (`/yayinlar/`)

- Üstte: "Google Scholar Profilim" buton
- Filtre: Yıl (select), Dergi (select), Sıralama (atıf/yıl)
- Liste: Her yayın kartı — APA format
- Her karta "Özet oku" butonu → Alpine.js modal → `Publication.abstract`
- "PubMed'de Aç" linki (`pubmed_id` varsa)
- Toplam atıf sayısı görünür (`sum(citation_count)`)

### 5.7 Sayfa: **Videolar** (`/videolar/`)

- Hero: Acıbadem resmi reel'i büyük (is_official_acibadem=True)
- Kategori filtre butonları (Alpine.js tab switcher)
- Grid: Thumbnail kartları, hover'da play ikonu
- Click → Modal ile embed oynat

### 5.8 Sayfa: **Blog** (`/blog/`)

- **Eğer hiç yayın yoksa:** "Yakında — Yeni yazılar için Instagram'dan takip edin: @dr.savasgundogan" placeholder. **Fake post oluşturma.**
- Varsa: Kategori filtreli grid + arama
- Detay: `/blog/<slug>/` — temiz uzun form okuma deneyimi, sağda "İlgili Uzmanlık" + "Randevu Al"

### 5.9 Sayfa: **SSS** (`/sss/`)

- Accordion (Alpine.js)
- Kategori grupları (varsa)
- Her cevapta ilgili video/uzmanlık linki

### 5.10 Sayfa: **İletişim** (`/iletisim/`)

- Sol: Form (ad, email, telefon opsiyonel, mesaj, KVKK checkbox)
- Sağ: Adres kartı + Google Maps iframe + e-posta + Acıbadem randevu butonu
- Alt: SSS cross-link
- Form HTMX ile submit edilir, inline success message gösterir
- `ContactMessage` modeline kaydedilir + opsiyonel olarak Murat'a e-posta gönderir (Django email backend, prod'da Resend/SendGrid)

### 5.11 Sayfa: **Gizlilik / KVKK** (`/gizlilik/`, `/aydinlatma-metni/`)

Statik sayfa, `DoctorProfile.kvkk_text` veya ayrı bir Page modeli ile dinamik. İlk kurulumda örnek KVKK metni seed et.

### 5.12 ❌ Eklenmeyecek Bölümler

- **Hasta Yorumları / Testimonials:** Gerçek yorum yok, FAKE yorum koyma. Hoca toplarsa sonra eklenir.
- **Ameliyat Öncesi/Sonrası Galeri:** Etik ve yasal izin gerektirir, Acıbadem onayı olmadan koyma.
- **Fiyat Listesi:** Özel hastane hekimi, fiyat verilmez.
- **Canlı chat / chatbot:** Şu an scope dışı.
- **Telemedicine portal:** Acıbadem'in kendi sistemi var, çakıştırma.

---

## 6. HEADER & FOOTER — ORTAK ELEMANLAR

### 6.1 Header (`_header.html`, sticky, backdrop-blur)

**Yükseklik:** 72px desktop, 64px mobile
**Arka plan:** `bg-white/90 backdrop-blur-md border-b border-gray-100` (scroll'da `shadow-sm` eklenir — Alpine.js ile)

**Düzen (desktop, sol → sağ):**
1. **Logo kısmı (sol):**
   - SVG logo (monogram "SG" + initials) + wordmark "Op. Dr. Savaş Gündoğan"
   - Altında küçük fareli text: "Acıbadem Maslak"
2. **Nav (orta, max-width içinde ortalı):**
   - Ana Sayfa | Hakkımda | Uzmanlık Alanlarım | Kariyer | Yayınlar | Videolar | Blog | SSS | İletişim
   - Active link: underline teal
   - Hover: teal renk + hafif translate-y-[-1px]
3. **Sağ aksiyonlar:**
   - Dil toggle (TR 🇹🇷 / EN 🇬🇧) — dropdown, Alpine.js
   - Instagram ikonu (link)
   - "Randevu Al" primary buton (teal, rounded-full)

**Mobile (<1024px):**
- Logo + Dil toggle + Hamburger
- Menü slide-in from right (Alpine.js + transition)
- Altta sabit `_floating_appointment.html` (her sayfada)

### 6.2 Footer (`_footer.html`)

4 kolon (desktop) → tek kolon (mobile):
1. **Marka kısmı:** Logo + `DoctorProfile.bio_short` (max 2 satır)
2. **Hızlı Linkler:** Tüm sayfalar
3. **İletişim:** Adres, e-posta, Acıbadem randevu, harita preview
4. **Sosyal & Akademik:** Instagram, Scholar, LinkedIn (varsa)

Alt şerit: `© 2026 Op. Dr. Savaş Gündoğan — Tüm Hakları Saklıdır. | KVKK | Gizlilik | Aydınlatma Metni`
İnce yazı: "Web tasarım: ..." (opsiyonel, senin için)

### 6.3 Global Partials

- `_floating_appointment.html`: Mobile için altta sabit tam genişlik "Randevu Al" buton (72px yükseklik), desktop'ta sağ alt köşe yuvarlak FAB
- `_cookie_banner.html`: İlk ziyarette alt şerit, KVKK onay, "Kabul Et" butonu, LocalStorage'da saklanır
- `_language_toggle.html`: Flag dropdown

---

## 7. TASARIM SİSTEMİ — "AI ÜRETİMİ GİBİ DURMASIN" KURALI

Bu en kritik bölüm. Aşağıdaki kuralları ihmal ETME.

### 7.1 Renk Paleti (tailwind.config.js'e ekle)

```js
colors: {
  teal: {
    50:  '#E6F7F8',
    100: '#B3E7EB',
    200: '#80D7DD',
    300: '#4DC7CF',
    400: '#26B7C1',
    500: '#00A0B0',   // ANA MARKA RENGİ
    600: '#008A99',
    700: '#007B8A',   // ACCENT
    800: '#005F6B',
    900: '#00434D',
  },
  cream: {
    50:  '#FDFCF9',   // Off-white arka plan
    100: '#F8F5EF',
    200: '#F0EBE0',
  },
  ink: {
    900: '#0F1720',   // Ana metin (saf siyah değil)
    700: '#3A4551',
    500: '#6B7582',
    300: '#B8BFC7',
    100: '#E8ECF0',
  },
  gold: {
    500: '#C9A961',   // Lüks accent (rozetler, altın dokunuşlar için)
    600: '#A88A48',
  }
}
```

**Kullanım kuralı:**
- Her yerde teal-500 kullanmak sıkıcı. Pop hissi için **gold** (rozetler, "Acıbadem Resmi" etiketleri, awards) ve **cream-50** (alternatif arka plan şeritleri) kullan.
- Metin rengi olarak saf siyah `#000` KULLANMA — `ink-900` (#0F1720) kullan. Saf siyah dijital'de sert görünür.

### 7.2 Typography

Self-hosted fontlar (Google Fonts yerine) — Vercel'de bandwidth ve GDPR için önemli:

```css
/* Headings */
font-family: 'Fraunces', 'Georgia', serif;
/* Fraunces: modern but has personality; "opsz" axis italic italic çok güzel */

/* Body */
font-family: 'Inter', system-ui, -apple-system, sans-serif;
/* Inter variable font */

/* Accent numerikler için (stats, yıllar) */
font-variant-numeric: tabular-nums;
font-feature-settings: 'ss01', 'cv11';
```

**Tailwind config:**
```js
fontFamily: {
  serif: ['"Fraunces Variable"', 'Georgia', 'serif'],
  sans: ['"Inter Variable"', 'system-ui', 'sans-serif'],
}
fontSize: {
  'hero': ['clamp(2.5rem, 5vw, 4.5rem)', { lineHeight: '1.05', letterSpacing: '-0.02em' }],
  'display': ['clamp(2rem, 4vw, 3.25rem)', { lineHeight: '1.1', letterSpacing: '-0.015em' }],
  // ...
}
```

**Hiyerarşi kuralı:**
- H1: Fraunces Medium, italic accent span'ler (örn: "Minimal *İnvaziv* Cerrahi")
- H2: Fraunces SemiBold
- H3: Inter Bold veya Fraunces Regular
- Body: Inter Regular 16-17px, line-height 1.65
- Stats / büyük sayılar: Fraunces Bold, tabular nums

### 7.3 Spacing & Layout

- Container max-width: `1200px` (ana), `760px` (blog okuma)
- Section vertical padding: `py-20 md:py-32` (cömert whitespace)
- Hero section: `min-h-[88vh]`
- Kartlar arası gap: `gap-8 md:gap-10` (12px yerine 40px cömert)

### 7.4 Animasyonlar (aşırıya kaçma)

- **Fade-up on scroll:** Intersection Observer + Alpine.js. Tüm section başlıklarında, threshold 0.15.
- **Hover transitions:** 250ms ease-out (200 değil, 250 daha "lüks")
- **Counter animasyonu:** İstatistiklerde, viewport'a girince 0'dan hedef sayıya
- **Image reveal:** Mask animation (clip-path) — hero görselde ve portrelerde
- **NO parallax on mobile** (performans + epilepsi)
- **NO auto-playing video with sound**
- **Reel embed:** muted by default

### 7.5 Bileşen Tasarım Kuralları

#### Butonlar
- Primary: teal-500 bg, white text, `rounded-full` (tam yuvarlak), py-3 px-8, hover'da teal-600 + subtle scale 1.02
- Secondary (outline): teal-500 border, teal-700 text, hover'da bg fill
- Tertiary (ghost): sadece altı çizili, teal text, hover'da altı tam çizili

#### Kartlar
- **Generic stok kart YASAK.** Aşağıdaki stillerden uygun olanı seç:
  - **Editorial kart:** Büyük görsel + sol üst köşede ince kategori etiketi + altta Fraunces başlık, ince ayırıcı çizgi, kısa metin
  - **Icon kart:** Sol üstte büyük teal rounded square içinde Lucide icon, altta başlık + açıklama, köşede ">" ok
  - **Featured kart (Acıbadem reel için):** Gold border outline + üst stcker etiketi
- Shadow: `shadow-none` default, hover'da `shadow-[0_20px_60px_-20px_rgba(0,160,176,0.25)]` (teal-tinted shadow)
- Border radius: `rounded-2xl` (16px) — **3xl yerine 2xl**, `rounded-lg` (8px) değil

#### Formlar
- Input: `border-b` (sadece alt çizgi, box değil), `focus:border-teal-500`, floating label
- Label: küçük uppercase letter-spacing-wide ink-500
- Submit: primary button

#### Listeler
- Bullet point yerine **ince teal çizgi** (`·` 2px) + 16px padding-left
- Liste öğeleri arası `space-y-3`

### 7.6 Tasarım Anti-Patterns — ASLA YAPMA

| ❌ Yapma | ✅ Yap |
|---|---|
| Bootstrap card + stock photo grid | Asymmetric editorial layout, gerçek doktor fotoğrafları |
| Sayfa boyunca aynı mavi | Teal + gold + cream kombinasyonu ile katmanlı palet |
| Her yerde emoji "🩺💉⚕️" | Lucide icons (stroke-width: 1.5) — minimal, tek renk |
| "Click here" tarzı genel CTA | Spesifik CTA: "Randevu için Acıbadem'e git", "Endometriozis videosunu izle" |
| Her section `bg-blue-50` | Cream-50 ve white alternatifleri, ince divider çizgiler |
| Stock hero background (dünya haritası, DNA helix) | Gerçek hoca fotoğrafı veya temiz tekstürlü cream pattern |
| Auto-playing carousel | Manuel pagination + swipe gesture (Embla veya Swiper) |
| `shadow-xl` everywhere | Soft shadow + hover'da depth |
| Sans-serif sadece | Serif (Fraunces) + Sans (Inter) mix |
| "Dr. Savaş" generic yazısı logoda | Custom monogram SVG |
| Tüm kartlar aynı boyut | **Bento grid** — mixed sizes (1x1, 1x2, 2x2) |
| Pure black `#000` text | Ink-900 `#0F1720` |
| Boyutsuz viewport | `min-h-[88vh]` hero, cömert dikey boşluk |

### 7.7 Bento Grid Özel Notu
Ana sayfadaki "Uzmanlık Alanlarım" için **bento grid** kullan — 6 kart aynı boyutta değil, 1 büyük (2x2) + 4 orta + 1 dikey. Bu modern, kişilikli görünüm sağlar. Apple, Linear, Vercel gibi siteler kullanıyor.

---

## 8. ADMIN PANELİ — İKİ AYRI DENEYİM

### 8.1 Murat Emre için `/admin/` (Django Jazzmin)

`config/settings/base.py` içinde:
```python
JAZZMIN_SETTINGS = {
    "site_title": "Dr. Savaş Gündoğan — Yönetim Paneli",
    "site_header": "Op. Dr. Savaş Gündoğan",
    "site_brand": "Admin",
    "welcome_sign": "Hoş geldin, admin.",
    "copyright": "Op. Dr. Savaş Gündoğan",
    "search_model": ["expertise.SpecialtyArea", "blog.BlogPost"],
    "topmenu_links": [
        {"name": "Siteyi Görüntüle", "url": "/", "new_window": True},
        {"name": "Doktor Paneli", "url": "/doctor-admin/", "permissions": ["auth.view_user"]},
    ],
    "icons": {
        "auth.User": "fas fa-user-shield",
        "core.DoctorProfile": "fas fa-user-md",
        "expertise.SpecialtyArea": "fas fa-stethoscope",
        "publications.Publication": "fas fa-book-medical",
        "media_library.Video": "fas fa-video",
        "blog.BlogPost": "fas fa-newspaper",
        "faq.FAQItem": "fas fa-question-circle",
    },
    "custom_css": "css/admin-custom.css",
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "theme": "cosmo",
    "dark_mode_theme": "darkly",
    "navbar_small_text": False,
    "accent": "accent-teal",
    "navbar": "navbar-white navbar-light",
}
```

Murat'a tüm modellere erişim (superuser). Tüm çok dilli alanları tabs ile göster.

### 8.2 Dr. Savaş için `/doctor-admin/` (Özel, Basit)

**Kullanıcı grubu:** `doctor_editors` (Django Group)
**Decorator:** `@login_required` + `@user_passes_test(lambda u: u.groups.filter(name='doctor_editors').exists() or u.is_superuser)`

**Dashboard (`/doctor-admin/`):**
- Üstte büyük karşılama: "Hoş geldiniz Op. Dr. Savaş"
- 6 büyük kart (her biri 180px yükseklik, büyük icon + etiket + "Git →"):
  1. 📝 Hakkımda Metnini Düzenle → `/doctor-admin/profile/`
  2. 🎓 Eğitim & Deneyim → `/doctor-admin/career/`
  3. 📚 Yayınlar → `/doctor-admin/publications/`
  4. 🎥 Videolar → `/doctor-admin/videos/`
  5. ✍️ Blog Yazıları → `/doctor-admin/blog/`
  6. ❓ SSS → `/doctor-admin/faq/`
- Alt: Son mesajlar (ContactMessage) — okunmamış olanların bildirimi
- Stats widget: "Bu ay site ziyareti", "En çok görüntülenen yayın" (Google Analytics API bağlarsak)

**Form sayfaları:**
- Büyük input kutuları (min 48px yükseklik)
- Dil sekmeleri üstte (TR / EN) — CKEditor her sekmede
- "Kaydet" butonu sağ altta sticky
- Başarı mesajı: yeşil toast 3 saniye
- Sadece kendi kontrolündeki modellere erişir; User, Group, SiteSettings'e erişim YOK.

**Özel view'lar:** `apps/doctor_admin/views.py` içinde Django generic CBV'ler (ListView, UpdateView, CreateView, DeleteView) — admin.py değil, custom templated.

**Template'ler:** `templates/doctor_admin/` — Tailwind + Alpine ile, site tasarımının admin versiyonu.

### 8.3 İlk Kullanıcıları Oluştur — Management Command

`apps/core/management/commands/create_initial_users.py`:
```python
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
import os

class Command(BaseCommand):
    def handle(self, *args, **opts):
        # Doktor grubu
        doctor_group, _ = Group.objects.get_or_create(name='doctor_editors')
        # (permissions eklenir — sadece ilgili modeller)

        # Superuser Murat
        if not User.objects.filter(username=os.getenv('ADMIN_SUPERUSER_USERNAME')).exists():
            User.objects.create_superuser(
                username=os.getenv('ADMIN_SUPERUSER_USERNAME'),
                email=os.getenv('ADMIN_SUPERUSER_EMAIL'),
                password=os.getenv('ADMIN_SUPERUSER_PASSWORD'),
            )

        # Doktor user
        if not User.objects.filter(username=os.getenv('DOCTOR_ADMIN_USERNAME')).exists():
            u = User.objects.create_user(
                username=os.getenv('DOCTOR_ADMIN_USERNAME'),
                email=os.getenv('DOCTOR_ADMIN_EMAIL'),
                password=os.getenv('DOCTOR_ADMIN_PASSWORD'),
                is_staff=True,
            )
            u.groups.add(doctor_group)
```

Deploy sonrası Vercel CLI ile `vercel env pull` + lokal `python manage.py create_initial_users` veya Supabase SQL editor'dan doğrudan ekle.

---

## 9. VERCEL DEPLOYMENT — SIFIRDAN

### 9.1 `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "config/wsgi.py",
      "use": "@vercel/python",
      "config": { "maxLambdaSize": "15mb", "runtime": "python3.12" }
    },
    {
      "src": "build_files.sh",
      "use": "@vercel/static-build",
      "config": { "distDir": "staticfiles_build" }
    }
  ],
  "routes": [
    { "src": "/static/(.*)", "dest": "/staticfiles_build/static/$1" },
    { "src": "/(.*)", "dest": "config/wsgi.py" }
  ]
}
```

### 9.2 `build_files.sh`
```bash
#!/bin/bash
set -e

# Python bağımlılıkları
pip install -r requirements.txt

# Frontend build (Tailwind)
npm install
npm run build  # package.json: "build": "tailwindcss -i ./static/src/css/input.css -o ./static/dist/css/output.css --minify"

# Django
python manage.py collectstatic --noinput --clear
python manage.py compilemessages || true  # translation dosyaları
python manage.py migrate --noinput
```

### 9.3 Environment Variables (Vercel Dashboard'da set edilir)
- `DJANGO_SECRET_KEY`
- `DJANGO_SETTINGS_MODULE=config.settings.prod`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=drsavasgundogan.vercel.app,drsavasgundogan.com`
- `DATABASE_URL` (Supabase pooler URL — pgbouncer connection string)
- `CLOUDINARY_URL` veya `CLOUDINARY_CLOUD_NAME/API_KEY/SECRET`
- `ADMIN_SUPERUSER_*` ve `DOCTOR_ADMIN_*` (ilk deploy için)

### 9.4 Supabase Postgres Kurulumu
1. supabase.com'da yeni proje aç
2. "Connect" → "Connection string" → "Transaction pooler" (port 6543, pgbouncer)
3. `DATABASE_URL` olarak Vercel'e ekle
4. Not: Session pooler (port 5432) yerine **Transaction pooler** (port 6543) kullan — Vercel serverless için uygun
5. Settings'te `CONN_MAX_AGE=0` (serverless'ta persistent connection yok)

### 9.5 Cloudinary Kurulumu
1. cloudinary.com'a kayıt ol
2. Dashboard → API Environment variable kopyala (`CLOUDINARY_URL=cloudinary://...`)
3. Vercel env'e ekle
4. `settings/prod.py` içinde:
```python
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

### 9.6 settings/prod.py Özel Ayarlar
```python
from .base import *
import dj_database_url

DEBUG = False
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=env('DATABASE_URL'),
        conn_max_age=0,  # Serverless — no persistent connections
        ssl_require=True,
    )
}

# Static files — WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Media — Cloudinary
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Security
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### 9.7 `dj-database-url` Ekleme
`requirements.txt`'e `dj-database-url==2.2.*` ekle (DATABASE_URL parsing için).

### 9.8 Vercel Gotchas / Bilinen Sorunlar
- **Lambda size limit 50MB:** Pillow + psycopg2-binary toplamda yaklaşık 30MB. Gerekirse `vercel.json`'da `maxLambdaSize: "15mb"` yerine "50mb" kullan.
- **Cold start:** İlk istek 2-3 saniye yavaş olabilir. Vercel Pro'da Fluid Compute ile iyileşiyor. Hobby plan için kabul edilebilir.
- **`compilemessages`:** gettext sistem kütüphanesi lazım; Vercel build image'ında yok. Çözüm: .po'ları lokal'de compile et, .mo'ları commit et (normalde gitignore'da ama Vercel için yapılacak). Alternatif: `--keep-pot` ile çalıştır ve hatayı swallow et (|| true).
- **`python manage.py migrate`:** Her deploy'da çalışır. Supabase'de migrations tablosu persistent.
- **Background tasks yok:** Celery çalışmaz. Email gönderimi için Resend API (sync HTTP call) kullan.

---

## 10. FRONTEND BUILD — TAILWIND

### 10.1 `package.json`
```json
{
  "name": "drsavasgundogan-frontend",
  "version": "1.0.0",
  "scripts": {
    "build": "tailwindcss -i ./static/src/css/input.css -o ./static/dist/css/output.css --minify",
    "watch": "tailwindcss -i ./static/src/css/input.css -o ./static/dist/css/output.css --watch"
  },
  "devDependencies": {
    "tailwindcss": "^3.4.14",
    "@tailwindcss/forms": "^0.5.9",
    "@tailwindcss/typography": "^0.5.15",
    "@tailwindcss/aspect-ratio": "^0.4.2"
  }
}
```

### 10.2 `tailwind.config.js`
```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
    './static/src/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: { /* bkz §7.1 */ },
      fontFamily: { /* bkz §7.2 */ },
      animation: {
        'fade-up': 'fadeUp 0.6s ease-out',
        'reveal': 'reveal 1.2s cubic-bezier(0.77, 0, 0.175, 1)',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
```

### 10.3 `static/src/css/input.css`
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  /* Self-hosted fonts */
  @font-face {
    font-family: 'Inter Variable';
    font-style: normal;
    font-weight: 100 900;
    font-display: swap;
    src: url('/static/fonts/inter-variable.woff2') format('woff2-variations');
  }
  @font-face {
    font-family: 'Fraunces Variable';
    font-style: normal;
    font-weight: 100 900;
    font-display: swap;
    src: url('/static/fonts/fraunces-variable.woff2') format('woff2-variations');
  }

  html { scroll-behavior: smooth; }
  body { @apply bg-cream-50 text-ink-900 font-sans antialiased; }
  ::selection { @apply bg-teal-500/20 text-teal-900; }
}

@layer components {
  .btn-primary {
    @apply inline-flex items-center justify-center gap-2 px-8 py-3.5
           bg-teal-500 text-white font-medium rounded-full
           transition-all duration-250 hover:bg-teal-600 hover:scale-[1.02]
           focus:outline-none focus:ring-4 focus:ring-teal-500/30;
  }

  .btn-outline {
    @apply inline-flex items-center justify-center gap-2 px-8 py-3.5
           border-2 border-teal-500 text-teal-700 font-medium rounded-full
           transition-all duration-250 hover:bg-teal-500 hover:text-white;
  }

  .section-padding {
    @apply py-20 md:py-28 lg:py-32;
  }

  .container-main {
    @apply max-w-[1200px] mx-auto px-6 lg:px-8;
  }

  .h-hero { @apply font-serif text-hero font-medium tracking-tight; }
  .h-display { @apply font-serif text-display font-medium tracking-tight; }

  .editorial-card {
    @apply bg-white rounded-2xl overflow-hidden transition-all duration-250
           hover:shadow-[0_20px_60px_-20px_rgba(0,160,176,0.25)]
           hover:-translate-y-1;
  }
}
```

### 10.4 HTML'de Static Dosyaları Yükle (base.html)
```html
{% load static %}
<link rel="stylesheet" href="{% static 'dist/css/output.css' %}">
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
<script src="https://unpkg.com/htmx.org@2.0.2" integrity="sha384-..." crossorigin="anonymous"></script>
```

(Üretimde Alpine ve HTMX de self-host edilebilir, ancak ilk iterasyonda CDN kabul edilebilir).

---

## 11. UYGULAMA SIRASI — CLAUDE CODE BU SIRAYI TAKİP ET

**Claude Code: Sırayı bozma. Her adımı tamamla, commit et, sonrakine geç.**

### Phase 1: İskelet (Tahmini 1 saat)
1. Venv aktifleştir (kullanıcı zaten hazır: `e:/WEBSITES/drsavasgundogan-v1/.venv/Scripts/Activate.ps1`)
2. `pip install -r requirements.txt` — önce requirements.txt yaz
3. `django-admin startproject config .`
4. Klasör yapısını oluştur (bkz §3)
5. `settings/base.py + dev.py + prod.py` yaz
6. `.env.example`, `.gitignore`, `.python-version` oluştur
7. `INITIAL COMMIT: project skeleton`

### Phase 2: Çekirdek Modeller (1-2 saat)
8. `apps/core` + `DoctorProfile` + `SiteSettings` + `ContactMessage`
9. `apps/experience` modelleri
10. `apps/expertise` modelleri
11. `apps/publications` modelleri
12. `apps/media_library` modelleri
13. `apps/blog` modelleri
14. `apps/faq` modelleri
15. Translation kayıtları (tüm `translation.py`)
16. `makemigrations` + `migrate` (SQLite)
17. `COMMIT: core models`

### Phase 3: Admin & İlk Veri (1-2 saat)
18. Jazzmin kurulumu + `ModelAdmin` sınıfları (her model için TabbedTranslationAdmin)
19. `create_initial_users` management command
20. Seed data management command — `seed_doctor_data` — önceki raporlardan tüm veriyi (eğitim, deneyim, 10+ publication, uzmanlık alanları) fixture olarak yükle
21. `COMMIT: admin + seed data`

### Phase 4: Frontend Build Sistemi (30 dk)
22. `package.json` + `tailwind.config.js` + `postcss.config.js`
23. `input.css` ile component classes
24. `npm run build` test
25. Self-hosted fontları indir (Inter Variable + Fraunces Variable) → `static/src/fonts/`
26. `COMMIT: frontend build setup`

### Phase 5: Template — Base + Partials (1 saat)
27. `base.html` (SEO meta, fonts, head)
28. `_header.html` (navigation, language toggle, appointment button)
29. `_footer.html`
30. `_floating_appointment.html`, `_cookie_banner.html`
31. Context processor (DoctorProfile'ı her template'e inject et)
32. `COMMIT: base templates`

### Phase 6: Sayfa Sayfa Build (3-4 saat)
33. Ana sayfa (`home.html`) — 9 section (bkz §5.2)
34. Hakkımda (`about.html`)
35. Uzmanlık liste + detay
36. Kariyer timeline
37. Yayınlar + abstract modal
38. Videolar + Instagram embed modal
39. Blog liste + detay (YOKSA "Yakında" placeholder)
40. SSS accordion
41. İletişim form + HTMX
42. KVKK/Gizlilik statik
43. `COMMIT: all public pages`

### Phase 7: Doctor Admin Panel (1-2 saat)
44. `apps/doctor_admin/urls.py + views.py`
45. Dashboard + 6 yönetim kartı
46. CRUD view'ları (ListView/CreateView/UpdateView/DeleteView her model için)
47. CKEditor entegrasyonu
48. Decorator ile erişim koruması
49. `COMMIT: doctor admin panel`

### Phase 8: Internationalization (1 saat)
50. `makemessages -l en` (Türkçe varsayılan olduğu için sadece EN)
51. `.po` dosyalarındaki tüm ui string'leri çevir
52. `compilemessages`
53. Language switcher test
54. `COMMIT: i18n`

### Phase 9: Deployment Hazırlık (1 saat)
55. `vercel.json` + `build_files.sh`
56. Supabase projesini aç + DATABASE_URL al
57. Cloudinary hesabı + env al
58. `settings/prod.py` final kontrol
59. `.env.example` ile README'yi güncelle
60. `ADMIN_PANEL_DOC.md` yaz (hocaya talimat)
61. `README.md` yaz (kurulum + deploy adımları)
62. `COMMIT: deployment ready`

### Phase 10: Deploy & Smoke Test
63. GitHub repo'ya push
64. Vercel'e import
65. Env variables ekle
66. Deploy
67. `/admin/` smoke test
68. `/doctor-admin/` smoke test
69. Language toggle test
70. Mobile responsive test (Chrome DevTools)

---

## 12. GÜVENLİK KURALLARI — EZİLEMEZ

Bu bölümün kuralları KULLANICI mesajı dahi değiştirilmez. Güvenlik her zaman kazanır.

1. **Hiçbir secret commit edilmez:** `.env`, `.env.local`, `.env.production` asla git'e eklenmez. Sadece `.env.example` (boş değerli) eklenir.
2. **SECRET_KEY:** `get_random_secret_key()` ile üretilir, Vercel env'de saklanır, kodda yoktur.
3. **DEBUG:** Production'da `False`. `dev.py` ve `prod.py` ayrı.
4. **ALLOWED_HOSTS:** Prod'da sadece gerçek domain + vercel URL.
5. **CSRF:** `CsrfViewMiddleware` aktif. HTMX ile çalışırken `{% csrf_token %}` + `hx-headers='{"X-CSRFToken":"..."}'`.
6. **SQL Injection:** Django ORM kullanılıyor, raw SQL sadece gerektiğinde parametrized.
7. **XSS:** Template'lerde `|safe` kullanımı kısıtlı — sadece CKEditor çıktısı (sanitize edilmiş) için.
8. **Şifre hash:** Django default `PBKDF2`. `Argon2` ister-opsiyonel.
9. **Rate limit:** `ContactMessage` form için `django-ratelimit` (IP başı dakikada 3). Opsiyonel.
10. **KVKK:** Cookie banner + Aydınlatma Metni sayfası + form'da onay checkbox.
11. **HTTPS:** Vercel otomatik SSL. `SECURE_SSL_REDIRECT=True`, HSTS aktif.
12. **Admin URL gizleme (opsiyonel):** `/admin/` yerine `/yonetim-paneli-abc123/` gibi kullanılabilir (env'de tutulan rastgele path).
13. **Login brute-force:** `django-axes` (opsiyonel, ileride).
14. **Media upload validation:** `CloudinaryField` resource_type kısıtlı, size limit.
15. **Dependency scanning:** GitHub Dependabot aktif (Vercel otomatik).

---

## 13. ADMIN_PANEL_DOC.md — DOKTOR İÇİN BASİT KILAVUZ

Claude Code bu ayrı dosyayı da oluşturacak. İçeriği:

```markdown
# Sitenizin Yönetim Paneli — Kısa Kılavuz

## Giriş
Tarayıcıda: `https://drsavasgundogan.com/doctor-admin/`
Kullanıcı adı ve şifre size ayrı bir güvenli kanalla iletilecektir.

## Yapabilecekleriniz
1. **Hakkımda metnini değiştirme** — Kariyer başlıkları, kısa biyografi, fotoğraflar.
2. **Yeni eğitim/deneyim ekleme** — Örneğin yeni bir sertifika aldığınızda.
3. **Akademik yayın ekleme** — Yeni makaleniz yayınlandığında tek formdan.
4. **Video ekleme** — Yeni bir Instagram Reel paylaştığınızda URL yapıştırın.
5. **Blog yazısı yazma** — Hasta bilgilendirme metinleri.
6. **SSS güncelleme** — Yeni sık sorular eklemek.
7. **Mesajları okuma** — Siteden gelen iletişim formları.

## Yapamayacaklarınız (Bilerek Kısıtlı)
- Kullanıcı hesapları (güvenlik için Murat yönetir)
- Site tasarımı / renk değişiklikleri
- Domain ve hosting ayarları

Her değişiklikten sonra sayfanın sağ altında yeşil bir "Kaydedildi" bildirimi göreceksiniz. Siteniz 10-30 saniye içinde otomatik güncellenir.

Sorun yaşarsanız: Murat Emre ile iletişime geçin.
```

---

## 14. README.md — GELİŞTİRİCİ (MURAT) İÇİN

Claude Code bu dosyayı da oluşturacak. En az şunları içersin:

1. Projenin ne olduğu
2. Tech stack
3. Lokal kurulum adımları (venv activate → pip install → npm install → migrate → runserver)
4. Ortam değişkenleri açıklaması
5. Deploy adımları
6. Supabase + Cloudinary setup talimatı
7. Admin erişimi nasıl alınır
8. Yeni uygulama/model eklerken dikkat edilecekler
9. Translation güncelleme (`makemessages` + `compilemessages`)
10. Troubleshooting (bilinen Vercel sorunları)

---

## 15. CLAUDE CODE İÇİN SON NOTLAR

### Karar verirken şu soruları sor:
1. **"Bu özellik gerçekten gerekli mi?"** — Feature creep'e düşme. Scope'u dar tut.
2. **"Bu sayfada gösterilecek gerçek veri var mı?"** — Yoksa sayfayı yapma.
3. **"Bu Vercel'de çalışır mı?"** — Filesystem write, background job, long request = YOK.
4. **"Bu secret leak eder mi?"** — .env dışında hiçbir yerde secret olmamalı.
5. **"Bu AI generic duruyor mu?"** — Varsa §7.6'ya bak ve yeniden tasarla.

### Yapma zaten:
- `print(...)` debug statement'ları production kodunda
- `TODO` ve `FIXME` yorumları — hallet veya issue aç
- Test için hardcoded data
- Fake lorem ipsum
- Placeholder stock photolar
- Testimonial / yorum bölümleri (EKLEME)
- Language hard-code (`"Randevu Al"` doğrudan template'de değil, `{% trans %}` ile)

### Önce sor, sonra yap:
Eğer bu dosyada belirsiz bir şey gördüğünde veya kullanıcıdan gelen yeni talebe bu dosyayla çelişen bir şey olduğunda, **önce sor** — varsayım yapma. Özellikle:
- Yeni bir bölüm / sayfa önerisi
- Güvenlik kurallarını değiştirecek talep
- Dış API / entegrasyon eklenmesi
- Design system'den sapma

### Her commit mesajı:
`<type>(<scope>): <summary>` formatında (Conventional Commits).
Örn: `feat(expertise): add specialty detail page with modal`

### Her PR öncesi checklist:
- [ ] `python manage.py check` temiz mi?
- [ ] `python manage.py makemigrations --dry-run --check` hata vermiyor mu?
- [ ] `npm run build` başarılı mı?
- [ ] `.env` değil, `.env.example` mı commit ettim?
- [ ] Yeni çevrilebilir string'ler için `makemessages` çalıştırdım mı?
- [ ] Admin paneli test edildi mi?

---

## 16. EK KAYNAKLAR (CLAUDE CODE SAAT TIKLADIĞI ZAMAN BUNLARA BAK)

- Django 5.2 docs: https://docs.djangoproject.com/en/5.2/
- django-modeltranslation: https://django-modeltranslation.readthedocs.io/
- django-jazzmin: https://django-jazzmin.readthedocs.io/
- Vercel + Django: https://vercel.com/templates/python/django-hello-world
- Supabase + Django: https://supabase.com/docs/guides/database/connecting-to-postgres
- Cloudinary Django: https://cloudinary.com/documentation/django_integration
- Tailwind docs: https://tailwindcss.com/docs
- Alpine.js: https://alpinejs.dev/
- HTMX: https://htmx.org/docs/
- Acıbadem Dr. Profili (TR): https://www.acibadem.com.tr/doktor/savas-gundogan/
- Acıbadem Dr. Profili (EN): https://www.acibadem.com.tr/en/doctor/savas-gundogan/
- Google Scholar: https://scholar.google.com/citations?user=9hUh--8AAAAJ&hl=en
- Instagram: https://www.instagram.com/dr.savasgundogan/
- Hero Instagram Reel (Acıbadem): https://www.instagram.com/reel/DUs9VxiDBej/

---

**Bu dosya son hali değildir — proje ilerledikçe güncellenecektir.**
**Sürüm:** 1.0 · **Tarih:** 16 Nisan 2026
**Yazar:** Murat Emre 
