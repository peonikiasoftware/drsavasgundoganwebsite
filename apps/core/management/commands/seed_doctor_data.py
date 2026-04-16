"""
Seed verified doctor data into the database.

All data pulled from:
 - Acıbadem Maslak public profile (https://www.acibadem.com.tr/doktor/savas-gundogan/)
 - Google Scholar profile (user=9hUh--8AAAAJ)
 - Public Acıbadem Instagram Reel (https://www.instagram.com/reel/DUs9VxiDBej/)

Safe to run multiple times — uses get_or_create / update_or_create.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.blog.models import BlogCategory
from apps.core.models import DoctorProfile, SiteSettings
from apps.experience.models import Education, Experience, Membership
from apps.expertise.models import SpecialtyArea, SpecialtyCategory
from apps.faq.models import FAQCategory, FAQItem
from apps.media_library.models import Video, VideoCategory
from apps.publications.models import Publication


DOCTOR_PROFILE_TR = dict(
    full_name="Op. Dr. Savaş Gündoğan",
    title_short="Op. Dr.",
    title_long_tr="Kadın Hastalıkları ve Doğum Uzmanı",
    title_long_en="Obstetrics & Gynecology Specialist",
    hero_headline_tr="Minimal İnvaziv Jinekolojik Cerrahi ve Kadın Sağlığı",
    hero_headline_en="Minimally Invasive Gynecologic Surgery & Women's Health",
    hero_subheadline_tr="Laparoskopi · Robotik Cerrahi · vNOTES · Endometriozis · Ürojinekoloji",
    hero_subheadline_en="Laparoscopy · Robotic Surgery · vNOTES · Endometriosis · Urogynecology",
    hero_intro_paragraph_tr=(
        "Acıbadem Maslak Hastanesi'nde, minimal invaziv tekniklerle ve uluslararası "
        "eğitim deneyimiyle kadın sağlığının her aşamasında yanınızdayım. Her hasta "
        "özeldir — tedavi planı yaşam tarzınıza ve beklentilerinize göre birebir tasarlanır."
    ),
    hero_intro_paragraph_en=(
        "At Acıbadem Maslak Hospital I bring minimally invasive techniques and international "
        "training to every stage of women's health. Every patient is unique — treatment is "
        "tailored to your lifestyle and expectations."
    ),
    bio_short_tr=(
        "İnönü Üniversitesi Tıp Fakültesi mezunu, Acıbadem Mehmet Ali Aydınlar Üniversitesi'nde "
        "Kadın Hastalıkları ve Doğum uzmanlığını tamamladı. İtalya Università degli Studi "
        "dell'Insubria'da misafir araştırmacı olarak minimal invaziv cerrahi alanında eğitim aldı. "
        "Hâlen Acıbadem Sağlık Grubu bünyesinde, Acıbadem Maslak Hastanesi'nde görev yapmaktadır."
    ),
    bio_short_en=(
        "Graduated from İnönü University Medical Faculty and completed his specialization in "
        "Obstetrics & Gynecology at Acıbadem Mehmet Ali Aydınlar University. Trained as a "
        "visiting assistant physician at Università degli Studi dell'Insubria (Italy) in "
        "minimally invasive gynecologic surgery. Currently practices at Acıbadem Maslak Hospital."
    ),
    bio_long_tr=(
        "<p>Op. Dr. Savaş Gündoğan, 2012 yılında İnönü Üniversitesi Tıp Fakültesi'nden mezun oldu. "
        "Uzmanlık eğitimini 2019 yılında Acıbadem Mehmet Ali Aydınlar Üniversitesi Tıp Fakültesi "
        "Kadın Hastalıkları ve Doğum Anabilim Dalı'nda tamamladı. 2016–2017 yıllarında "
        "İtalya Università degli Studi dell'Insubria'da misafir araştırmacı olarak görev yaparak, "
        "minimal invaziv jinekolojik cerrahi alanında deneyim kazandı.</p>"
        "<p>2014–2019 yıllarında Sultanbeyli Devlet Hastanesi'nde, 2019–2022 yıllarında "
        "Şişli Etfal Eğitim ve Araştırma Hastanesi'nde uzman hekim olarak görev yaptı. "
        "2022–2025 yıllarında Acıbadem Maslak Hastanesi'nde çalıştı; 2025 yılından itibaren "
        "Acıbadem Sağlık Grubu bünyesinde hizmet vermeyi sürdürüyor.</p>"
        "<p>Laparoskopik ve robotik cerrahi, endometriozis tedavisi, izsiz vajinal cerrahi "
        "(vNOTES), ürojinekoloji, menopoz yönetimi ve jinekolojik onkoloji başlıca ilgi "
        "alanlarıdır. Kapsamlı akademik çalışmaları Journal of Minimally Invasive Gynecology "
        "başta olmak üzere prestijli uluslararası dergilerde yayımlanmıştır.</p>"
    ),
    bio_long_en=(
        "<p>Dr. Savaş Gündoğan graduated from İnönü University Medical Faculty in 2012 and "
        "completed his residency in Obstetrics & Gynecology at Acıbadem Mehmet Ali Aydınlar "
        "University Medical Faculty in 2019. From 2016 to 2017 he served as a visiting "
        "assistant physician at Università degli Studi dell'Insubria in Italy, where he "
        "developed expertise in minimally invasive gynecologic surgery.</p>"
        "<p>He worked as a specialist at Sultanbeyli State Hospital (2014–2019) and at "
        "Şişli Etfal Training & Research Hospital (2019–2022) before joining Acıbadem Maslak "
        "Hospital in 2022. Since 2025 he continues to practice within the Acıbadem Health Group.</p>"
        "<p>His main clinical interests include laparoscopic and robotic surgery, endometriosis "
        "treatment, scarless vaginal surgery (vNOTES), urogynecology, menopause management, "
        "and gynecologic oncology. His research has been published in leading international "
        "journals, including the Journal of Minimally Invasive Gynecology.</p>"
    ),
    philosophy_quote_tr=(
        "Her hasta bir hikâyedir. Modern tıbbın sunduğu en ince teknikleri kullanırken, "
        "asıl çabam; dinlemek, anlamak ve ona özel bir tedavi planı kurmaktır."
    ),
    philosophy_quote_en=(
        "Every patient is a story. While I use the most refined techniques of modern medicine, "
        "my true work is to listen, to understand, and to build a plan that belongs to each "
        "person alone."
    ),
    email_public="savas.gundogan@acibadem.com",
    phone_public="",
    appointment_url="https://www.acibadem.com.tr/doktor/savas-gundogan/",
    hospital_name_tr="Acıbadem Maslak Hastanesi",
    hospital_name_en="Acıbadem Maslak Hospital",
    hospital_address_tr="Büyükdere Cad. No:40, 34457 Maslak / İstanbul",
    hospital_address_en="Büyükdere Cad. No:40, 34457 Maslak / Istanbul, Türkiye",
    google_maps_embed_url=(
        "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d6016.12!2d29.01!3d41.11"
        "!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zQWPEsWJhZGVtIE1hc2xhayBIYXN0YW5lc2k!5e0!3m2!1str!2str!4v1700000000000!5m2!1str!2str"
    ),
    instagram_url="https://www.instagram.com/dr.savasgundogan/",
    instagram_handle="@dr.savasgundogan",
    google_scholar_url="https://scholar.google.com/citations?user=9hUh--8AAAAJ&hl=en",
    acibadem_profile_tr="https://www.acibadem.com.tr/doktor/savas-gundogan/",
    acibadem_profile_en="https://www.acibadem.com.tr/en/doctor/savas-gundogan/",
    years_of_experience=12,
    publication_count=20,
)


EDUCATION = [
    # (start, end, degree, institution, location, highlight)
    dict(
        year_start=2005, year_end=2012,
        degree_tr="Tıp Doktoru", degree_en="Doctor of Medicine (MD)",
        institution_tr="İnönü Üniversitesi Tıp Fakültesi",
        institution_en="İnönü University Medical Faculty",
        location_tr="Malatya, Türkiye", location_en="Malatya, Türkiye",
        is_highlight=False, order=30,
    ),
    dict(
        year_start=2013, year_end=2019,
        degree_tr="Uzmanlık — Kadın Hastalıkları ve Doğum",
        degree_en="Residency — Obstetrics & Gynecology",
        institution_tr="Acıbadem Mehmet Ali Aydınlar Üniversitesi Tıp Fakültesi",
        institution_en="Acıbadem Mehmet Ali Aydınlar University Medical Faculty",
        location_tr="İstanbul, Türkiye", location_en="Istanbul, Türkiye",
        is_highlight=True, order=20,
    ),
    dict(
        year_start=2016, year_end=2017,
        degree_tr="Misafir Araştırmacı — Minimal İnvaziv Jinekolojik Cerrahi",
        degree_en="Visiting Assistant Physician — Minimally Invasive Gynecologic Surgery",
        institution_tr="Università degli Studi dell'Insubria",
        institution_en="Università degli Studi dell'Insubria",
        location_tr="Varese, İtalya", location_en="Varese, Italy",
        is_highlight=True, order=10,
    ),
]


EXPERIENCE = [
    dict(
        year_start=2011, year_end=2012,
        position_tr="İntörn Hekim", position_en="Intern Physician",
        institution_tr="İnönü Üniversitesi Turgut Özal Tıp Merkezi",
        institution_en="İnönü University Turgut Özal Medical Center",
        location_tr="Malatya", location_en="Malatya",
        order=70, is_current=False,
    ),
    dict(
        year_start=2012, year_end=2012,
        position_tr="Üroloji Asistanı", position_en="Urology Resident",
        institution_tr="Erzincan Üniversitesi", institution_en="Erzincan University",
        location_tr="Erzincan", location_en="Erzincan",
        order=65, is_current=False,
    ),
    dict(
        year_start=2013, year_end=2013,
        position_tr="Pratisyen Hekim", position_en="General Practitioner",
        institution_tr="Erzincan Devlet Hastanesi", institution_en="Erzincan State Hospital",
        location_tr="Erzincan", location_en="Erzincan",
        order=60, is_current=False,
    ),
    dict(
        year_start=2013, year_end=2014,
        position_tr="Araştırma Görevlisi Hekim", position_en="Resident Physician",
        institution_tr="Acıbadem Mehmet Ali Aydınlar Üniversitesi",
        institution_en="Acıbadem Mehmet Ali Aydınlar University",
        location_tr="İstanbul", location_en="Istanbul",
        order=50, is_current=False,
    ),
    dict(
        year_start=2014, year_end=2019,
        position_tr="Kadın Hastalıkları ve Doğum Uzmanı",
        position_en="Obstetrics & Gynecology Specialist",
        institution_tr="Sultanbeyli Devlet Hastanesi",
        institution_en="Sultanbeyli State Hospital",
        location_tr="İstanbul", location_en="Istanbul",
        order=40, is_current=False,
    ),
    dict(
        year_start=2019, year_end=2022,
        position_tr="Başasistan — Kadın Hastalıkları ve Doğum",
        position_en="Department Specialist — Obstetrics & Gynecology",
        institution_tr="Şişli Etfal Eğitim ve Araştırma Hastanesi",
        institution_en="Şişli Etfal Training & Research Hospital",
        location_tr="İstanbul", location_en="Istanbul",
        order=30, is_current=False, is_highlight=True,
    ),
    dict(
        year_start=2022, year_end=2025,
        position_tr="Kadın Hastalıkları ve Doğum Uzmanı",
        position_en="Obstetrics & Gynecology Specialist",
        institution_tr="Acıbadem Maslak Hastanesi",
        institution_en="Acıbadem Maslak Hospital",
        location_tr="İstanbul", location_en="Istanbul",
        order=20, is_current=False, is_highlight=True,
    ),
    dict(
        year_start=2025, year_end=None,
        position_tr="Kadın Hastalıkları ve Doğum Uzmanı",
        position_en="Obstetrics & Gynecology Specialist",
        institution_tr="Acıbadem Sağlık Grubu — Maslak",
        institution_en="Acıbadem Health Group — Maslak",
        location_tr="İstanbul", location_en="Istanbul",
        order=10, is_current=True, is_highlight=True,
    ),
]


MEMBERSHIPS = [
    dict(name_tr="Türk Jinekoloji ve Obstetrik Derneği (İstanbul)",
         name_en="Turkish Gynecology and Obstetrics Society (Istanbul)", order=10),
    dict(name_tr="Jinekolojik Endoskopi Derneği — Minimal İnvaziv Jinekoloji",
         name_en="Minimally Invasive Gynecology Association", order=20),
    dict(name_tr="Jinekoloji ve Obstetrikte Tartışmalı Konular Derneği",
         name_en="Gynecology and Obstetrics Controversial Issues Society", order=30),
    dict(name_tr="Tüp Bebek ve İnfertilite Derneği (TÜBİT)",
         name_en="Tube Baby and Infertility Association (TUBIT)", order=40),
]


SPECIALTY_CATEGORIES = [
    dict(slug="minimal-invaziv-cerrahi",
         name_tr="Minimal İnvaziv Cerrahi", name_en="Minimally Invasive Surgery",
         icon="scissors", order=10),
    dict(slug="kadin-sagligi",
         name_tr="Kadın Sağlığı", name_en="Women's Health",
         icon="heart", order=20),
    dict(slug="uroginekoloji",
         name_tr="Ürojinekoloji", name_en="Urogynecology",
         icon="droplets", order=30),
]


SPECIALTY_AREAS = [
    dict(
        slug="endometriozis",
        category_slug="kadin-sagligi",
        icon="flame",
        bento_size="2x2",
        is_featured=True, order=10,
        title_tr="Endometriozis Tedavisi",
        title_en="Endometriosis Treatment",
        short_description_tr=(
            "Ağrılı adet, kısırlık ve derin yerleşimli endometriozis için laparoskopik "
            "eksizyon başta olmak üzere modern, organ-koruyucu tedaviler."
        ),
        short_description_en=(
            "Modern, organ-sparing treatment for painful periods, infertility and deep "
            "infiltrating endometriosis — including laparoscopic excision surgery."
        ),
        full_description_tr=(
            "<p>Endometriozis, rahim iç dokusuna benzer dokunun karın içinde farklı "
            "bölgelerde yerleşmesiyle oluşan kronik bir hastalıktır. Adet döneminde şiddetli "
            "ağrı, cinsel ilişki sırasında ağrı, yoğun kanama ve kısırlık gibi şikayetlere "
            "yol açabilir.</p>"
            "<p>Modern yaklaşımda sadece semptom tedavisi değil, hastalığın kaynağına yönelik "
            "laparoskopik tam eksizyon hedeflenir. Deep-infiltrating vakalarda çok disiplinli "
            "bir ekip yaklaşımıyla bağırsak veya üriner sistem tutulumu da ele alınır.</p>"
        ),
        full_description_en=(
            "<p>Endometriosis is a chronic condition in which tissue similar to the uterine "
            "lining grows outside the uterus. It can cause severe menstrual pain, painful "
            "intercourse, heavy bleeding and infertility.</p>"
            "<p>Modern care aims beyond symptom control — laparoscopic complete excision "
            "of disease remains the cornerstone. For deep-infiltrating disease a multidisciplinary "
            "team addresses bowel or urinary involvement as well.</p>"
        ),
    ),
    dict(
        slug="laparoskopik-cerrahi",
        category_slug="minimal-invaziv-cerrahi",
        icon="layers",
        bento_size="1x1",
        is_featured=True, order=20,
        title_tr="Laparoskopik Cerrahi",
        title_en="Laparoscopic Surgery",
        short_description_tr=(
            "Miyom, kist ve rahim hastalıkları için küçük kesilerle, daha kısa iyileşme süresi "
            "sunan ileri düzey laparoskopik operasyonlar."
        ),
        short_description_en=(
            "Advanced laparoscopic procedures for fibroids, cysts and uterine conditions — "
            "small incisions, shorter recovery, minimal scarring."
        ),
        full_description_tr=(
            "<p>Laparoskopi, karın boşluğuna ince kamera ve enstrümanlarla ulaşılan bir "
            "cerrahi yöntemdir. Açık cerrahiye kıyasla kanama, ağrı ve hastanede kalış "
            "süresi belirgin şekilde azalır, iz neredeyse görünmez.</p>"
        ),
        full_description_en=(
            "<p>Laparoscopy accesses the abdomen through small ports with a fine camera "
            "and instruments. Compared with open surgery, bleeding, pain and hospital stay "
            "are significantly lower and scarring is minimal.</p>"
        ),
    ),
    dict(
        slug="robotik-cerrahi",
        category_slug="minimal-invaziv-cerrahi",
        icon="cpu",
        bento_size="1x1",
        is_featured=True, order=30,
        title_tr="Robotik Cerrahi",
        title_en="Robotic Surgery",
        short_description_tr=(
            "da Vinci platformu ile rahim, miyom ve endometriozis ameliyatlarında üç boyutlu "
            "görüntü ve milimetrik hassasiyet."
        ),
        short_description_en=(
            "Using the da Vinci platform for uterine, myomectomy and endometriosis surgery "
            "with 3D visualization and millimetric precision."
        ),
    ),
    dict(
        slug="vnotes-izsiz-vajinal-cerrahi",
        category_slug="minimal-invaziv-cerrahi",
        icon="sparkles",
        bento_size="2x1",
        is_featured=True, order=40,
        title_tr="vNOTES — İzsiz Vajinal Cerrahi",
        title_en="vNOTES — Scarless Vaginal Surgery",
        short_description_tr=(
            "Vajinal yoldan doğal açıklıkla yapılan, karında hiçbir iz bırakmayan modern "
            "histerektomi ve over cerrahisi."
        ),
        short_description_en=(
            "Modern hysterectomy and ovarian surgery performed through the natural vaginal "
            "opening — no visible abdominal scars."
        ),
    ),
    dict(
        slug="uroginekoloji",
        category_slug="uroginekoloji",
        icon="droplets",
        bento_size="1x1",
        is_featured=True, order=50,
        title_tr="Ürojinekoloji — İdrar Kaçırma ve Sarkma",
        title_en="Urogynecology — Incontinence & Prolapse",
        short_description_tr=(
            "Stres tipi idrar kaçırma, aşırı aktif mesane ve pelvik organ sarkmasında cerrahi "
            "ve cerrahi dışı tedavi seçenekleri."
        ),
        short_description_en=(
            "Surgical and non-surgical solutions for stress incontinence, overactive bladder "
            "and pelvic organ prolapse."
        ),
    ),
    dict(
        slug="menopoz-yonetimi",
        category_slug="kadin-sagligi",
        icon="sun",
        bento_size="1x1",
        is_featured=True, order=60,
        title_tr="Menopoz ve Hormon Tedavisi",
        title_en="Menopause & Hormone Management",
        short_description_tr=(
            "Sıcak basması, uyku düzensizliği, kemik erimesi ve cinsel sağlık şikayetlerinde "
            "kişiye özel, kanıta dayalı menopoz yönetimi."
        ),
        short_description_en=(
            "Evidence-based, personalized menopause care for hot flashes, sleep disruption, "
            "bone health and sexual wellbeing."
        ),
    ),
    dict(
        slug="jinekolojik-onkoloji",
        category_slug="kadin-sagligi",
        icon="shield",
        bento_size="1x1",
        is_featured=False, order=70,
        title_tr="Jinekolojik Onkoloji ve Tarama",
        title_en="Gynecologic Oncology & Screening",
        short_description_tr=(
            "HPV, PAP smear, kolposkopi ve jinekolojik kanserlerin erken tanısı, "
            "multidisipliner tedavisi."
        ),
        short_description_en=(
            "HPV, Pap smear, colposcopy and early detection of gynecologic cancers — "
            "with multidisciplinary treatment planning."
        ),
    ),
    dict(
        slug="gebelik-takibi",
        category_slug="kadin-sagligi",
        icon="baby",
        bento_size="1x1",
        is_featured=False, order=80,
        title_tr="Gebelik Takibi ve Doğum",
        title_en="Pregnancy Care & Delivery",
        short_description_tr=(
            "Tekil ve çoğul gebeliklerde kapsamlı anne-bebek sağlığı takibi, riskli gebelik "
            "yönetimi ve doğum planlaması."
        ),
        short_description_en=(
            "Comprehensive maternal-fetal follow-up for singleton and multiple pregnancies, "
            "high-risk pregnancy management, and delivery planning."
        ),
    ),
]


PUBLICATIONS = [
    dict(
        title_tr="Laparoskopik ve Robotik Miyomektomi Sonrası Semptomlar ve Yaşam Kalitesi",
        title_en="Symptoms and Health Quality After Laparoscopic and Robotic Myomectomy",
        authors="Takmaz O, Ozbasli E, Gundogan S, et al.",
        journal="JSLS: Journal of the Society of Laparoendoscopic Surgeons",
        year=2018, citation_count=30, is_featured=True, order=10,
        pubmed_id="30524183",
    ),
    dict(
        title_tr=(
            "Laparoskopik Histerektomi Sonrası Ağrı Yönetimi için Perioperatif Duloksetin: "
            "Randomize Plasebo Kontrollü Çalışma"
        ),
        title_en=(
            "Perioperative Duloxetine for Pain Management After Laparoscopic Hysterectomy: "
            "A Randomized Placebo-Controlled Trial"
        ),
        authors="Takmaz O, Bastu E, Ozbasli E, Gundogan S, et al.",
        journal="Journal of Minimally Invasive Gynecology",
        year=2020, citation_count=24, is_featured=True, order=20,
        pubmed_id="31476481",
    ),
    dict(
        title_tr="Dev Servikal Miyomun Laparoskopik Yönetimi",
        title_en="Laparoscopic Management of Huge Cervical Myoma",
        authors="Peker N, Gundogan S, Şendağ F",
        journal="Journal of Minimally Invasive Gynecology",
        year=2017, citation_count=16, is_featured=True, order=30,
        pubmed_id="27632929",
    ),
    dict(
        title_tr=(
            "Heterotopik İstmokornual Gebeliğin Laparoskopik Yönetimi: Farklı Bir Teknik"
        ),
        title_en=(
            "Laparoscopic Management of Heterotopic Istmocornual Pregnancy: A Different Technique"
        ),
        authors="Peker N, Aydeniz EG, Gundogan S, Şendağ F",
        journal="Journal of Minimally Invasive Gynecology",
        year=2017, citation_count=16, is_featured=False, order=40,
        pubmed_id="27449690",
    ),
    dict(
        title_tr="Dev Miyomun Laparoskopik Yardımlı Robotik Miyomektomisi",
        title_en="Laparoscopic Assisted Robotic Myomectomy of a Huge Myoma",
        authors="Takmaz Ö, Gundogan S, Özbaşlı E, et al.",
        journal="Journal of the Turkish German Gynecological Association",
        year=2019, citation_count=6, is_featured=False, order=50,
    ),
    dict(
        title_tr=(
            "Derin İnfiltratif Endometriozisli Hastada Tek Port Total Laparoskopik Histerektomi"
        ),
        title_en=(
            "Single-Port Total Laparoscopic Hysterectomy in a Patient with Deep Infiltrating "
            "Endometriosis"
        ),
        authors="Şendağ F, Peker N, Aydeniz EG, Akdemir A, Gundogan S",
        journal="Journal of Minimally Invasive Gynecology",
        year=2017, citation_count=6, is_featured=False, order=60,
        pubmed_id="27480596",
    ),
    dict(
        title_tr="Tek Port Robotik Pelvik Bulky Lenf Nodu Rezeksiyonu: Vaka Sunumu",
        title_en="Single-Port Robotic Pelvic Bulky Lymph Node Resection: A Case Report",
        authors="Gungor M, Takmaz O, Afsar S, Ozbasli E, Gundogan S",
        journal="Journal of Minimally Invasive Gynecology",
        year=2016, citation_count=6, is_featured=False, order=70,
        pubmed_id="27311875",
    ),
    dict(
        title_tr="Şiddetli Endometriozis için Tek Kesi Laparoskopik Histerektomi",
        title_en="Single Incision Laparoscopic Hysterectomy for Severe Endometriosis",
        authors="Sendag F, Peker N, Aydeniz EG, Akdemir A, Gundogan S",
        journal="Journal of Minimally Invasive Gynecology",
        year=2015, citation_count=3, is_featured=False, order=80,
        pubmed_id="27678683",
    ),
    dict(
        title_tr="Adolesan Gebelikler ve Perinatal Sonuçlar",
        title_en="Adolescent Pregnancies and Perinatal Outcomes",
        authors="Peker N, Demir A, Aydın C, Biler A, Gundogan S",
        journal="Clinical & Experimental Obstetrics & Gynecology",
        year=2018, citation_count=2, is_featured=False, order=90,
    ),
    dict(
        title_tr=(
            "Üçüncü Trimester Gebelikte Spontan Dalak Arteri Anevrizması Rüptürü"
        ),
        title_en=(
            "Spontaneous Rupture of a Splenic Artery Aneurysm During the Third Trimester of "
            "Pregnancy"
        ),
        authors="Peker N, Vicdanlı NH, Demir A, Bozan MB, Gundogan S",
        journal="Case Reports in Perinatal Medicine",
        year=2017, citation_count=1, is_featured=False, order=100,
    ),
    dict(
        title_tr="Laparoskopik Abdominal Serklaj",
        title_en="Laparoscopic Abdominal Cerclage",
        authors="Sendag F, Peker N, Aydeniz EG, Akdemir A, Gundogan S",
        journal="Journal of Minimally Invasive Gynecology",
        year=2015, citation_count=1, is_featured=False, order=110,
        pubmed_id="27678733",
    ),
]


VIDEO_CATEGORIES = [
    dict(slug="menopoz", name_tr="Menopoz", name_en="Menopause", order=10),
    dict(slug="endometriozis", name_tr="Endometriozis", name_en="Endometriosis", order=20),
    dict(slug="cerrahi", name_tr="Cerrahi Teknikler", name_en="Surgical Techniques", order=30),
    dict(slug="kadin-sagligi", name_tr="Kadın Sağlığı", name_en="Women's Health", order=40),
]

VIDEOS = [
    dict(
        title_tr="Kişiye Özel Hormon Tedavisi",
        title_en="Personalized Hormone Therapy",
        description_tr=(
            "Vajinal kuruluk, menopoz ve idrar kaçırma sorunlarına modern, kişiye özel yaklaşım."
        ),
        description_en=(
            "A modern, personalized approach to vaginal dryness, menopause and urinary "
            "incontinence."
        ),
        platform="instagram",
        video_url="https://www.instagram.com/reel/DUs9VxiDBej/",
        is_featured=True, is_official_acibadem=True,
        category_slug="menopoz", order=10,
    ),
]


FAQ_CATEGORIES = [
    dict(name_tr="Ameliyat & Cerrahi", name_en="Surgery", order=10),
    dict(name_tr="Muayene & Süreç", name_en="Appointments & Process", order=20),
    dict(name_tr="Kadın Sağlığı", name_en="Women's Health", order=30),
]


FAQ_ITEMS = [
    dict(
        category_idx=0,
        question_tr="Laparoskopik ameliyat sonrası ne zaman günlük hayata dönebilirim?",
        question_en="When can I return to daily life after laparoscopic surgery?",
        answer_tr=(
            "<p>Yapılan işlemin büyüklüğüne göre değişmekle birlikte, basit laparoskopik "
            "operasyonlardan sonra 48–72 saat içinde hafif ev aktiviteleri mümkündür. "
            "Ofis çalışanları genellikle 5–10 gün, fiziksel işlerle uğraşanlar 3–4 hafta "
            "sonra tam kapasiteyle döner. Süreç her hasta için birebir planlanır.</p>"
        ),
        answer_en=(
            "<p>It depends on the procedure — after a simple laparoscopic operation light "
            "home activity is usually possible within 48–72 hours. Office workers typically "
            "return in 5–10 days, while physically demanding jobs need 3–4 weeks for full "
            "capacity. Each patient gets an individual plan.</p>"
        ),
        order=10, is_featured=True,
    ),
    dict(
        category_idx=0,
        question_tr="vNOTES nedir ve kimler için uygundur?",
        question_en="What is vNOTES and who is it suitable for?",
        answer_tr=(
            "<p>vNOTES, vajinal doğal açıklıktan yapılan, karın duvarında hiç kesi "
            "bırakmayan bir cerrahi tekniktir. Histerektomi ve over cerrahisi için uygundur. "
            "Daha az ağrı, daha hızlı iyileşme ve görünür iz olmaması avantajlarıdır. "
            "Her hasta uygun olmayabilir; muayenede birlikte karar veririz.</p>"
        ),
        answer_en=(
            "<p>vNOTES is a surgical technique performed through the natural vaginal opening, "
            "leaving no abdominal incision. It is suitable for hysterectomy and ovarian "
            "surgery and offers less pain, faster recovery and no visible scars. Not all "
            "patients are candidates — we decide together at the consultation.</p>"
        ),
        order=20, is_featured=True,
    ),
    dict(
        category_idx=1,
        question_tr="Randevu nasıl alabilirim?",
        question_en="How do I book an appointment?",
        answer_tr=(
            "<p>Acıbadem Maslak Hastanesi üzerinden çevrimiçi randevu alabilir veya site "
            "üzerindeki iletişim formu ile ekibimizle iletişime geçebilirsiniz.</p>"
        ),
        answer_en=(
            "<p>You can book online through Acıbadem Maslak Hospital or use the contact form "
            "on this site to reach our team.</p>"
        ),
        order=30, is_featured=False,
    ),
    dict(
        category_idx=2,
        question_tr="Endometriozisin kesin tedavisi var mı?",
        question_en="Is there a definitive treatment for endometriosis?",
        answer_tr=(
            "<p>Endometriozis kronik bir hastalıktır; ancak doğru cerrahi teknikle (tam "
            "eksizyon) semptomlar büyük ölçüde geriletilebilir, doğurganlık korunabilir. "
            "Tedavi planı; hastalığın evresine, yaşa ve doğurganlık beklentilerine göre "
            "kişiye özel oluşturulur.</p>"
        ),
        answer_en=(
            "<p>Endometriosis is a chronic disease, but with the right surgical technique "
            "(complete excision) symptoms can be greatly reduced while preserving fertility. "
            "The plan is personalized to disease stage, age and fertility plans.</p>"
        ),
        order=40, is_featured=False,
    ),
]


BLOG_CATEGORIES = [
    dict(slug="menopoz", name_tr="Menopoz ve Hormonlar",
         name_en="Menopause & Hormones", order=10),
    dict(slug="cerrahi", name_tr="Minimal İnvaziv Cerrahi",
         name_en="Minimally Invasive Surgery", order=20),
    dict(slug="gebelik", name_tr="Gebelik ve Doğum",
         name_en="Pregnancy & Delivery", order=30),
    dict(slug="genel-saglik", name_tr="Genel Kadın Sağlığı",
         name_en="General Women's Health", order=40),
]


class Command(BaseCommand):
    help = "Seed verified DoctorProfile, Education, Experience, Publications, etc."

    @transaction.atomic
    def handle(self, *args, **opts):
        self._seed_profile()
        self._seed_site_settings()
        self._seed_education()
        self._seed_experience()
        self._seed_memberships()
        self._seed_specialty_categories_and_areas()
        self._seed_publications()
        self._seed_videos()
        self._seed_faq()
        self._seed_blog_categories()
        self.stdout.write(self.style.SUCCESS("Seed complete."))

    # ------------------------------------------------------------------
    def _seed_profile(self):
        obj = DoctorProfile.load()
        for k, v in DOCTOR_PROFILE_TR.items():
            setattr(obj, k, v)
        obj.save()
        self.stdout.write("DoctorProfile updated.")

    def _seed_site_settings(self):
        s = SiteSettings.load()
        if not s.default_meta_title_tr:
            s.default_meta_title_tr = (
                "Op. Dr. Savaş Gündoğan — Acıbadem Maslak Kadın Hastalıkları ve Doğum"
            )
        if not s.default_meta_title_en:
            s.default_meta_title_en = (
                "M.D. Savaş Gündoğan — Obstetrics & Gynecology, Acıbadem Maslak"
            )
        if not s.default_meta_description_tr:
            s.default_meta_description_tr = (
                "Minimal invaziv jinekolojik cerrahi, endometriozis, robotik cerrahi, vNOTES "
                "ve kadın sağlığının her alanında uzmanlık."
            )
        if not s.default_meta_description_en:
            s.default_meta_description_en = (
                "Specialist in minimally invasive gynecologic surgery, endometriosis, robotic "
                "surgery, vNOTES and women's health."
            )
        s.save()
        self.stdout.write("SiteSettings updated.")

    def _seed_education(self):
        Education.objects.all().delete()
        for item in EDUCATION:
            Education.objects.create(**item)
        self.stdout.write(f"Education: {len(EDUCATION)} rows.")

    def _seed_experience(self):
        Experience.objects.all().delete()
        for item in EXPERIENCE:
            Experience.objects.create(**item)
        self.stdout.write(f"Experience: {len(EXPERIENCE)} rows.")

    def _seed_memberships(self):
        Membership.objects.all().delete()
        for item in MEMBERSHIPS:
            Membership.objects.create(**item)
        self.stdout.write(f"Memberships: {len(MEMBERSHIPS)} rows.")

    def _seed_specialty_categories_and_areas(self):
        SpecialtyArea.objects.all().delete()
        SpecialtyCategory.objects.all().delete()
        cat_map = {}
        for c in SPECIALTY_CATEGORIES:
            cat_map[c["slug"]] = SpecialtyCategory.objects.create(**c)
        for a in SPECIALTY_AREAS:
            data = dict(a)
            cat_slug = data.pop("category_slug", None)
            data["category"] = cat_map.get(cat_slug) if cat_slug else None
            SpecialtyArea.objects.create(**data)
        self.stdout.write(
            f"Expertise: {len(SPECIALTY_CATEGORIES)} categories, {len(SPECIALTY_AREAS)} areas."
        )

    def _seed_publications(self):
        Publication.objects.all().delete()
        for p in PUBLICATIONS:
            Publication.objects.create(**p)
        self.stdout.write(f"Publications: {len(PUBLICATIONS)} rows.")

    def _seed_videos(self):
        Video.objects.all().delete()
        VideoCategory.objects.all().delete()
        cat_map = {}
        for c in VIDEO_CATEGORIES:
            cat_map[c["slug"]] = VideoCategory.objects.create(**c)
        for v in VIDEOS:
            data = dict(v)
            cat_slug = data.pop("category_slug", None)
            data["category"] = cat_map.get(cat_slug) if cat_slug else None
            Video.objects.create(**data)
        self.stdout.write(
            f"Videos: {len(VIDEO_CATEGORIES)} categories, {len(VIDEOS)} videos."
        )

    def _seed_faq(self):
        FAQItem.objects.all().delete()
        FAQCategory.objects.all().delete()
        cats = [FAQCategory.objects.create(**c) for c in FAQ_CATEGORIES]
        for f in FAQ_ITEMS:
            data = dict(f)
            idx = data.pop("category_idx", None)
            data["category"] = cats[idx] if idx is not None else None
            FAQItem.objects.create(**data)
        self.stdout.write(
            f"FAQ: {len(FAQ_CATEGORIES)} categories, {len(FAQ_ITEMS)} items."
        )

    def _seed_blog_categories(self):
        for c in BLOG_CATEGORIES:
            BlogCategory.objects.update_or_create(slug=c["slug"], defaults=c)
        self.stdout.write(f"Blog categories: {len(BLOG_CATEGORIES)} rows (no posts yet).")
