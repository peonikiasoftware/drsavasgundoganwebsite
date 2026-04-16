# Op. Dr. Savaş Gündoğan — Resmi Web Sitesi

Django 5.2 (Python 3.12) + Tailwind CSS + HTMX + Alpine.js tabanlı,
iki dilli (TR/EN), Vercel üzerinde serverless olarak çalışan resmi web
sitesi.

Canlı site: `https://drsavasgundogan.com` (deploy sonrası)
Acıbadem profili: <https://www.acibadem.com.tr/doktor/savas-gundogan/>

---

## Mimari Özet

| Katman | Teknoloji |
|---|---|
| Backend | Django 5.2 LTS, Python 3.12 |
| DB (dev) | SQLite (`db.sqlite3`) |
| DB (prod) | Supabase PostgreSQL (Transaction pooler, port 6543) |
| Media (prod) | Cloudinary (serverless ephemeral FS için zorunlu) |
| Static | WhiteNoise + `collectstatic` → `staticfiles_build/` |
| Frontend | Django templates + Tailwind CSS (npm build) + Alpine.js + HTMX |
| Çeviri | `django-modeltranslation` (DB), `gettext` (.po/.mo) — TR varsayılan |
| Admin | Jazzmin (/admin) + özel Doktor Paneli (/doctor-admin) |
| Hosting | Vercel (GitHub push → auto deploy) |

---

## Lokal Kurulum

### 1. Prerequisites
- Python 3.12, Node.js 18+, npm
- (Opsiyonel) GNU gettext — `makemessages` / `compilemessages` için

### 2. Ortam değişkenleri
```bash
cp .env.example .env
# .env dosyasını düzenle:
#   DJANGO_SECRET_KEY  — `python -c "import secrets; print(secrets.token_urlsafe(50))"` ile üret
#   DATABASE_URL       — prod için Supabase URL; dev'de boş bırak (SQLite kullanılır)
#   CLOUDINARY_*       — prod için gerekli; dev'de boş → lokal FS kullanılır
#   ADMIN_SUPERUSER_*  — ilk superuser (Murat) için kullanılır
#   DOCTOR_ADMIN_*     — ilk doktor kullanıcısı (Savaş) için kullanılır
```

### 3. Python bağımlılıkları
```bash
# Venv zaten var: .venv/
./.venv/Scripts/Activate.ps1      # PowerShell
# veya
source .venv/Scripts/activate      # bash/Git Bash

pip install -r requirements.txt           # prod paketi
pip install -r requirements-dev.txt       # dev araçları (opsiyonel)
```

### 4. Frontend build
```bash
npm install
npm run build           # one-off Tailwind build (→ static/dist/css/output.css)
npm run watch           # geliştirme sırasında hot-rebuild
```

### 5. Database & seed
```bash
python manage.py migrate
python manage.py create_initial_users     # murat_admin + dr_savas user'ları
python manage.py seed_doctor_data         # tüm içerik (profil, yayınlar, vb.)
```

### 6. Çalıştır
```bash
python manage.py runserver
# http://127.0.0.1:8000/  (otomatik /tr/ veya /en/'e yönlendirir)
# http://127.0.0.1:8000/admin/         (Murat — superuser)
# http://127.0.0.1:8000/doctor-admin/  (Dr. Savaş)
```

---

## Deploy (Vercel)

### Tek seferlik kurulum
1. **Supabase** projesi aç, **Transaction pooler** (port 6543) connection
   string'ini kopyala.
2. **Cloudinary** hesabı aç; `CLOUDINARY_CLOUD_NAME / API_KEY / API_SECRET`
   değerlerini kopyala.
3. GitHub repo'ya push et.
4. `vercel.com/new` → GitHub repo'yu import et.
5. Project Settings → Environment Variables:
   ```
   DJANGO_SECRET_KEY=<strong random>
   DJANGO_SETTINGS_MODULE=config.settings.prod
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=<proje>.vercel.app,drsavasgundogan.com
   DATABASE_URL=postgresql://...
   CLOUDINARY_CLOUD_NAME=...
   CLOUDINARY_API_KEY=...
   CLOUDINARY_API_SECRET=...
   ADMIN_SUPERUSER_USERNAME=murat_admin
   ADMIN_SUPERUSER_EMAIL=...
   ADMIN_SUPERUSER_PASSWORD=<strong>
   DOCTOR_ADMIN_USERNAME=dr_savas
   DOCTOR_ADMIN_EMAIL=...
   DOCTOR_ADMIN_PASSWORD=<strong>
   EMAIL_HOST=smtp.resend.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=resend
   EMAIL_HOST_PASSWORD=<Resend API key>
   DEFAULT_FROM_EMAIL=no-reply@drsavasgundogan.com
   CONTACT_NOTIFICATION_EMAIL=mrtemroztrk@gmail.com
   ```
6. Deploy. İlk build ~3 dakika sürer.

### Post-deploy
- İlk deploy'dan sonra Vercel CLI ile tek sefer:
  ```
  vercel env pull
  python manage.py create_initial_users
  python manage.py seed_doctor_data
  ```
- Veya Supabase SQL editor'da `auth_user` satırlarını kontrol et;
  eksikse `/admin/` üzerinden normal `createsuperuser` çalıştır.

### Her deploy'da otomatik olarak çalışır
`build_files.sh` script'i:
1. `pip install -r requirements.txt`
2. `npm ci && npm run build`
3. `python manage.py collectstatic --noinput --clear`
4. `python manage.py migrate --noinput`
5. `python manage.py compilemessages` (best-effort — gettext yoksa swallow)

> **Bilinen Vercel sorunu:** gettext sistem kütüphanesi Vercel build
> image'ında yoktur. Bu yüzden `.mo` dosyaları repo'da commit edilir
> (bkz. `locale/*/LC_MESSAGES/*.mo`). Değişiklik yaptığında lokalde
> `python manage.py compilemessages` çalıştır ve .mo'yu commit et.

---

## Çeviri Güncelleme

```bash
# Kaynak TR string'lerden EN .po dosyasını güncelle
python manage.py makemessages -l en --ignore=.venv --ignore=node_modules

# locale/en/LC_MESSAGES/django.po içindeki msgstr satırlarını doldur

python manage.py compilemessages
git add locale/ && git commit -m "i18n: update en translations"
```

Gettext yoksa (Windows):
- Python stdlib'indeki `Tools/i18n/msgfmt.py` scripti ile compile et.

---

## Dizin Yapısı

```
drsavasgundogan-v1/
├── config/              # Django settings paketi (base/dev/prod) + wsgi/urls
├── apps/                # 8 Django app
│   ├── core/            # DoctorProfile, SiteSettings, ContactMessage, home, about
│   ├── experience/      # Education, Experience, Membership
│   ├── expertise/       # SpecialtyCategory, SpecialtyArea
│   ├── publications/    # Publication
│   ├── media_library/   # Video, VideoCategory
│   ├── blog/            # BlogPost, BlogCategory
│   ├── faq/             # FAQItem, FAQCategory
│   └── doctor_admin/    # /doctor-admin/ — doktor için özel dashboard
├── templates/           # DIR tabanlı template'ler (APP_DIRS False için)
├── static/
│   ├── src/             # Kaynak CSS/JS — git'e dahil
│   └── dist/            # Tailwind build çıktısı — gitignored
├── locale/              # .po + .mo — hepsi commitlenir
├── requirements.txt     # prod
├── requirements-dev.txt # dev
├── tailwind.config.js
├── package.json
├── vercel.json
├── build_files.sh
├── manage.py
├── .env.example         # şablon — commit edilir
├── .env                 # lokal — commit EDİLMEZ
└── CLAUDE.md            # ana tasarım + mimari dokümanı
```

---

## Ana Kullanıcılar

| Kullanıcı | Rol | Erişim |
|---|---|---|
| `murat_admin` | Superuser (Murat Emre) | `/admin/` + `/doctor-admin/` — full access |
| `dr_savas` | Doctor editor (Dr. Savaş Gündoğan) | `/doctor-admin/` (içerik yönetimi) |

Dr. Savaş kullanıcısı `doctor_editors` grubundadır; yalnızca içerik
modellerine (Publication, Video, BlogPost, FAQ, Education, Experience,
Membership) erişebilir. User/Group, SiteSettings gibi teknik
modellere erişimi yoktur.

---

## Hata Giderme

### "ckeditor.W001" uyarısı
django-ckeditor 6.x, CKEditor 4'ü kullanıyor. Güvenlik açısından zararsız
(yerel admin-only field), ancak uyarı görünür. İleride
`django-ckeditor-5`'e geçiş yapılabilir.

### Vercel deploy'da "Lambda size > 50MB"
`vercel.json` içinde `maxLambdaSize: "50mb"`. Pillow + psycopg2-binary ~30MB.
Daha büyük olursa `psycopg[binary]` yerine başka driver dene.

### "no module named 'psycopg2'"
Prod'da `psycopg2-binary` kullanılır (requirements.txt). pg_config
Vercel'de olmadığı için kesinlikle `psycopg2-binary` olmalı.

### Supabase bağlantı sorunu
Pooler (port **6543**) kullan, Session pooler (5432) değil. `CONN_MAX_AGE=0`
(prod.py içinde zaten ayarlı).

### Cloudinary upload hatası
`CLOUDINARY_*` env var'ları Vercel'de set edilmiş mi? Dev'de Cloudinary
yoksa `DEFAULT_FILE_STORAGE` otomatik olarak lokal FS'e düşer.

---

## İletişim & Bakım

- **Geliştirici:** Murat Emre — `mrtemroztrk@gmail.com`
- **Doktor kullanımı kılavuzu:** bkz. [`ADMIN_PANEL_DOC.md`](./ADMIN_PANEL_DOC.md)
- **Proje manifesto / karar günlüğü:** [`CLAUDE.md`](./CLAUDE.md)

---

© 2026 Op. Dr. Savaş Gündoğan
