"""Phase 2 content fill — blog posts, the new video, extra FAQ.

Idempotent. Safe to re-run. Skips anything that already exists.

Run:
    python manage.py fill_content_phase2
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.blog.models import BlogCategory, BlogPost
from apps.core.models import DoctorProfile
from apps.expertise.models import SpecialtyArea
from apps.faq.models import FAQCategory, FAQItem
from apps.media_library.models import Video, VideoCategory


# =====================================================================
# VIDEO — YouTube — Kişiye Özel Hormon Tedavisi
# =====================================================================
YOUTUBE_VIDEO = {
    "video_url": "https://www.youtube.com/watch?v=1WCty72ABdE",
    "platform": "youtube",
    "is_featured": True,
    "is_official_acibadem": True,
    "title_tr": "Kişiye Özel Hormon Tedavisi — Vajinal Sağlık",
    "title_en": "Personalized Hormone Therapy — Vaginal Health",
    "description_tr": (
        "Vajinal kuruluk, ağrılı cinsel ilişki ve idrar yakınmaları; yaşla birlikte "
        "azalan östrojen hormonuna bağlı olarak ortaya çıkabilir. Güncel bilimsel "
        "çalışmalar, bu şikâyetlerin tedavisinde lokal östrojenin etkili ve güvenli "
        "olduğunu göstermektedir. Uzun yıllar tartışma konusu olan güvenlik endişeleri, "
        "FDA'nın son açıklamalarıyla netlik kazanmıştır.\n\n"
        "Bugün klinik uygulamalarda, lokal östrojen ve östrojen dışı tedaviler hekim "
        "kontrolünde ve kişiye özel olarak güvenle kullanılabilmektedir. Vajinal sağlık, "
        "yaşam kalitesinin önemli bir parçasıdır. Doğru bilgi ve doğru tedaviyle çözüm "
        "mümkündür.\n\n"
        "Acıbadem Maslak Hastanesi Kadın Hastalıkları ve Doğum Uzmanı Op. Dr. Savaş "
        "Gündoğan, kişiye özel hormon tedavisi hakkında bilgilendiriyor."
    ),
    "description_en": (
        "Vaginal dryness, painful intercourse, and urinary complaints can arise from "
        "age-related decline in estrogen. Recent scientific evidence confirms that "
        "local estrogen is both effective and safe in treating these symptoms. "
        "Long-standing safety concerns have been clarified by the FDA's latest "
        "statements.\n\n"
        "In current clinical practice, local estrogen and non-estrogen therapies can "
        "be safely used in a personalized manner under physician supervision. Vaginal "
        "health is a meaningful part of quality of life — with the right information "
        "and the right treatment, solutions are within reach.\n\n"
        "M.D. Savaş Gündoğan, Specialist in Obstetrics and Gynecology at Acıbadem "
        "Maslak Hospital, explains personalized hormone therapy."
    ),
}


# =====================================================================
# BLOG POSTS — five published professional posts
# =====================================================================
BLOG_POSTS = [
    {
        "slug": "kisiye-ozel-hormon-tedavisi",
        "category_name": "Menopoz",
        "related_specialty_slug": "menopoz-yonetimi",
        "read_time_minutes": 5,
        "is_featured": True,
        "title_tr": "Kişiye Özel Hormon Tedavisi: Menopoz Dönemi İçin Modern Yaklaşım",
        "title_en": "Personalized Hormone Therapy: A Modern Approach to Menopause",
        "excerpt_tr": (
            "Menopozla birlikte gelen vajinal kuruluk, ağrılı ilişki ve idrar yakınmaları "
            "kadın hayatını derinden etkileyebilir. Güncel bilimsel kanıtlar, kişiye özel "
            "lokal hormon tedavisinin hem etkili hem güvenli olduğunu ortaya koyuyor."
        ),
        "excerpt_en": (
            "Menopausal vaginal dryness, painful intercourse, and urinary complaints can "
            "deeply affect women's lives. Current scientific evidence shows that "
            "personalized local hormone therapy is both effective and safe."
        ),
        "content_tr": (
            "<p>Menopoz, kadın hayatında doğal bir geçiş dönemidir. Ancak bu dönemde yaşanan "
            "vajinal kuruluk, cinsel ilişkide ağrı, idrar yolu enfeksiyonlarında artış ve "
            "idrar sıkışıklığı gibi şikâyetler yaşam kalitesini olumsuz etkileyebilir. "
            "Bu belirtilerin temel nedeni, vücutta azalan östrojen hormonudur.</p>"

            "<h3>Lokal Östrojenin Etkinliği ve Güvenliği</h3>"
            "<p>Yıllar boyunca hormon tedavileri ile ilgili güvenlik endişeleri tartışılmıştır. "
            "Ancak son dönemde yayımlanan kapsamlı bilimsel çalışmalar ve Amerikan Gıda ve "
            "İlaç Dairesi'nin (FDA) güncel açıklamaları, lokal östrojen kullanımının "
            "güvenlik profilini netleştirmiştir. Vajinal yolla uygulanan düşük doz "
            "östrojenin sistemik yan etkileri minimumdur ve uygun hastalarda güvenle "
            "kullanılabilir.</p>"

            "<h3>Kişiye Özel Planlama Nedir?</h3>"
            "<p>Her kadının tıbbi geçmişi, genel sağlık durumu ve beklentileri farklıdır. "
            "Kişiye özel hormon tedavisi yaklaşımında şu adımlar izlenir:</p>"
            "<ul>"
            "<li>Detaylı tıbbi öykü ve aile öyküsü değerlendirmesi</li>"
            "<li>Meme muayenesi ve mamografi kontrolü</li>"
            "<li>Hormon düzeylerinin ve genel laboratuvar parametrelerinin analizi</li>"
            "<li>Tedavi hedeflerinin birlikte belirlenmesi</li>"
            "<li>Lokal veya sistemik seçenekler arasında doğru tercihin yapılması</li>"
            "</ul>"

            "<h3>Östrojen Dışı Seçenekler</h3>"
            "<p>Östrojen kullanımı uygun görülmeyen hastalarda vajinal nem sağlayıcıları, "
            "hyalüronik asit bazlı ürünler, lazer uygulamaları ve belirli östrojen dışı "
            "oral tedaviler alternatif olarak değerlendirilir. Her seçenek, risk-fayda "
            "dengesi içinde değerlendirilerek planlanır.</p>"

            "<h3>Ne Zaman Hekime Başvurmalısınız?</h3>"
            "<p>Menopoza bağlı belirtiler yaşam kalitenizi etkiliyorsa — uyku, cinsel yaşam, "
            "günlük aktiviteler — tek başınıza geçiştirmek zorunda değilsiniz. Erken "
            "değerlendirme, hem belirtilerin yönetimini hem de uzun dönem kemik ve "
            "kardiyovasküler sağlığınızın korunmasını sağlar.</p>"

            "<p><em>Bu yazı genel bilgilendirme amaçlıdır ve kişisel tıbbi tavsiye yerine "
            "geçmez. Size uygun tedavinin belirlenmesi için randevu alarak muayene olmanızı "
            "öneririm.</em></p>"
        ),
        "content_en": (
            "<p>Menopause is a natural transition in a woman's life. Yet the symptoms it "
            "brings — vaginal dryness, painful intercourse, recurrent urinary infections, "
            "and urinary urgency — can meaningfully affect quality of life. The underlying "
            "cause is the decline in estrogen.</p>"

            "<h3>The Efficacy and Safety of Local Estrogen</h3>"
            "<p>Safety concerns about hormone therapy have been debated for years. Recent "
            "comprehensive studies and updated statements from the U.S. Food and Drug "
            "Administration (FDA) have clarified the safety profile of local estrogen. "
            "Low-dose vaginal estrogen has minimal systemic side effects and can be used "
            "safely in appropriate patients.</p>"

            "<h3>What Does 'Personalized' Mean?</h3>"
            "<p>Every woman's medical history, overall health, and expectations differ. "
            "A personalized approach follows these steps:</p>"
            "<ul>"
            "<li>Detailed medical and family history review</li>"
            "<li>Breast examination and mammography</li>"
            "<li>Analysis of hormone levels and relevant laboratory parameters</li>"
            "<li>Joint definition of treatment goals</li>"
            "<li>Selecting between local and systemic options based on individual fit</li>"
            "</ul>"

            "<h3>Non-Estrogen Alternatives</h3>"
            "<p>For patients in whom estrogen is not appropriate, vaginal moisturizers, "
            "hyaluronic-acid-based products, laser treatments, and certain non-estrogen "
            "oral therapies serve as alternatives. Each option is assessed within a "
            "risk-benefit framework.</p>"

            "<h3>When to See a Doctor</h3>"
            "<p>If menopausal symptoms are affecting your quality of life — your sleep, "
            "your sexual life, your daily activities — you do not need to cope alone. "
            "Early evaluation both manages symptoms and helps preserve your long-term "
            "bone and cardiovascular health.</p>"

            "<p><em>This article is for general information and does not replace "
            "personalized medical advice. Please schedule an appointment for an "
            "evaluation tailored to you.</em></p>"
        ),
        "meta_title_tr": "Kişiye Özel Hormon Tedavisi ve Menopoz — Dr. Savaş Gündoğan",
        "meta_title_en": "Personalized Hormone Therapy for Menopause — Dr. Savaş Gündoğan",
        "meta_description_tr": "Menopoz belirtilerinde kişiye özel lokal östrojen ve östrojen dışı tedaviler. Etkinlik, güvenlik ve uygulama.",
        "meta_description_en": "Personalized local estrogen and non-estrogen therapies for menopausal symptoms — efficacy, safety, and application.",
    },
    {
        "slug": "endometriozis-erken-tani",
        "category_name": "Endometriozis",
        "related_specialty_slug": "endometriozis",
        "read_time_minutes": 6,
        "is_featured": True,
        "title_tr": "Endometriozis: Neden Erken Tanı Hayat Kurtarır?",
        "title_en": "Endometriosis: Why Early Diagnosis Matters",
        "excerpt_tr": (
            "Her 10 kadından birini etkileyen endometriozisin tanısı ortalama 7 yıl gecikebilir. "
            "Hangi belirtiler yıllarca göz ardı edilmemeli ve modern tedavi seçenekleri neler?"
        ),
        "excerpt_en": (
            "Affecting one in ten women, endometriosis takes an average of seven years to be "
            "diagnosed. Which symptoms should never be dismissed — and what modern treatments exist?"
        ),
        "content_tr": (
            "<p>Endometriozis, rahim iç tabakasına benzer dokunun rahim dışında — yumurtalıklar, "
            "tüpler, bağırsaklar veya mesane üzerinde — büyümesi sonucu ortaya çıkan kronik bir "
            "hastalıktır. Her ay adet döngüsüne eşlik eden bu dokular kanar, iltihaplanır ve "
            "zamanla yapışıklıklara neden olabilir.</p>"

            "<h3>Neden Geç Tanı Alıyor?</h3>"
            "<p>Çalışmalar, endometriozisin tanı süresinin ortalama 7 yıl olduğunu gösteriyor. "
            "Bunun en önemli nedenleri:</p>"
            "<ul>"
            "<li>Şiddetli adet ağrısının 'normal' olarak kabul edilmesi</li>"
            "<li>Belirtilerin bireyden bireye büyük farklılık göstermesi</li>"
            "<li>Rutin görüntüleme yöntemlerinin her vakayı yakalayamaması</li>"
            "<li>Hastaların konforsuzluklarını paylaşmaktan çekinmesi</li>"
            "</ul>"

            "<h3>Dikkat Edilmesi Gereken Belirtiler</h3>"
            "<p>Aşağıdaki belirtiler bir araya geldiğinde muhakkak değerlendirilmelidir:</p>"
            "<ul>"
            "<li>Yıllar içinde şiddeti artan adet ağrısı</li>"
            "<li>Cinsel ilişki sırasında derin pelvik ağrı</li>"
            "<li>Adet dönemi dışında kronik pelvik ağrı</li>"
            "<li>Adet dönemlerinde tuvalete çıkarken ağrı</li>"
            "<li>Bir yıldan uzun süredir gebelik sağlanamaması</li>"
            "<li>Sürekli yorgunluk ve sindirim sistemi düzensizlikleri</li>"
            "</ul>"

            "<h3>Modern Tedavi Yaklaşımları</h3>"
            "<p>Endometriozis tedavisi hastanın yaşına, belirtilerinin şiddetine, çocuk sahibi "
            "olma isteğine ve hastalığın evresine göre planlanır. Günümüzde üç ana tedavi "
            "kolonu vardır:</p>"
            "<ol>"
            "<li><strong>Medikal tedavi:</strong> Hormonal ilaçlar ve ağrı kontrolü</li>"
            "<li><strong>Minimal invaziv cerrahi:</strong> Laparoskopi, robotik cerrahi veya "
            "seçilmiş olgularda vNOTES ile endometriotik odakların hassasiyetle temizlenmesi</li>"
            "<li><strong>Doğurganlık desteği:</strong> Gerektiğinde üremeye yardımcı tedaviler "
            "ile birlikte koordineli yönetim</li>"
            "</ol>"

            "<h3>Erken Tanının Değeri</h3>"
            "<p>Erken tanı, hem hastalığın ilerlemesini yavaşlatır hem de doğurganlığın "
            "korunması açısından kritik bir fırsat sunar. Şiddetli adet ağrısı yaşıyorsanız, "
            "'normaldir' diye susmayın — deneyimli bir jinekologa danışmak ilk adımdır.</p>"

            "<p><em>Bu yazı bilgilendirme amaçlıdır. Kişisel değerlendirme için randevu "
            "alabilirsiniz.</em></p>"
        ),
        "content_en": (
            "<p>Endometriosis is a chronic condition in which tissue similar to the uterine lining "
            "grows outside the uterus — on the ovaries, fallopian tubes, bowel, or bladder. These "
            "tissues bleed and inflame with every cycle and can form adhesions over time.</p>"

            "<h3>Why Is Diagnosis Often Delayed?</h3>"
            "<p>Studies show an average diagnostic delay of seven years. The main reasons:</p>"
            "<ul>"
            "<li>Severe menstrual pain being considered 'normal'</li>"
            "<li>Symptoms varying widely from patient to patient</li>"
            "<li>Routine imaging sometimes missing the disease</li>"
            "<li>Patients hesitating to share intimate discomfort</li>"
            "</ul>"

            "<h3>Symptoms That Deserve Attention</h3>"
            "<p>When the following symptoms cluster together, evaluation is essential:</p>"
            "<ul>"
            "<li>Menstrual pain that worsens over years</li>"
            "<li>Deep pelvic pain during intercourse</li>"
            "<li>Chronic pelvic pain outside of menstruation</li>"
            "<li>Painful urination or bowel movements during periods</li>"
            "<li>Difficulty conceiving for more than a year</li>"
            "<li>Persistent fatigue and gastrointestinal irregularity</li>"
            "</ul>"

            "<h3>Modern Treatment Approaches</h3>"
            "<p>Treatment is shaped by the patient's age, symptom severity, fertility goals, and "
            "disease stage. Three principal pillars guide care:</p>"
            "<ol>"
            "<li><strong>Medical therapy:</strong> hormonal medications and pain management</li>"
            "<li><strong>Minimally invasive surgery:</strong> laparoscopy, robotic surgery, or — "
            "in selected cases — vNOTES for precise removal of endometriotic foci</li>"
            "<li><strong>Fertility support:</strong> coordinated management with assisted "
            "reproduction when indicated</li>"
            "</ol>"

            "<h3>The Value of Early Diagnosis</h3>"
            "<p>Early diagnosis slows disease progression and preserves a critical window for "
            "fertility. If you are experiencing severe menstrual pain, do not dismiss it as "
            "'normal' — consulting an experienced gynecologist is the first step.</p>"

            "<p><em>This article is informational. Schedule an appointment for a personalized "
            "evaluation.</em></p>"
        ),
        "meta_title_tr": "Endometriozis: Erken Tanı ve Modern Tedavi — Dr. Savaş Gündoğan",
        "meta_title_en": "Endometriosis: Early Diagnosis and Modern Treatment",
        "meta_description_tr": "Endometriozis belirtileri, tanı süreci ve minimal invaziv tedavi seçenekleri. Dr. Savaş Gündoğan anlatıyor.",
        "meta_description_en": "Endometriosis symptoms, diagnostic process, and minimally invasive treatment options.",
    },
    {
        "slug": "minimal-invaziv-cerrahi-nedir",
        "category_name": "Cerrahi Teknikler",
        "related_specialty_slug": "laparoskopik-cerrahi",
        "read_time_minutes": 5,
        "is_featured": False,
        "title_tr": "Minimal İnvaziv Cerrahi Nedir? Laparoskopi, Robotik ve vNOTES",
        "title_en": "What Is Minimally Invasive Surgery? Laparoscopy, Robotics, and vNOTES",
        "excerpt_tr": (
            "Açık cerrahiye kıyasla daha az ağrı, daha kısa iyileşme süresi ve daha iyi estetik "
            "sonuçlar sunan minimal invaziv cerrahi tekniklerin temel farkları nelerdir?"
        ),
        "excerpt_en": (
            "Minimally invasive surgery offers less pain, faster recovery, and better "
            "aesthetic outcomes than open surgery. What are the key differences between "
            "the techniques?"
        ),
        "content_tr": (
            "<p>Son 20 yılda jinekolojik cerrahide yaşanan en büyük dönüşüm, minimal invaziv "
            "tekniklerin gelişmesidir. Bu yaklaşımlar; büyük kesiler yerine birkaç milimetrelik "
            "deliklerden veya doğal vücut açıklıklarından ameliyat yapılmasını sağlar.</p>"

            "<h3>Laparoskopi</h3>"
            "<p>Laparoskopik cerrahide karına 5-10 mm'lik 3-4 küçük kesi yapılır. Bir kameradan "
            "alınan yüksek çözünürlüklü görüntü ekrana yansıtılır. Myom, kist, endometriozis "
            "ve histerektomi gibi pek çok işlem güvenle yapılabilir.</p>"
            "<p><strong>Avantajlar:</strong> az ağrı, kısa hastanede kalış (genellikle 1 gün), "
            "hızlı iyileşme (1-2 hafta), küçük izler.</p>"

            "<h3>Robotik Cerrahi</h3>"
            "<p>Robotik platform, cerrahın konsolda oturarak 3 boyutlu ve büyütmeli görüntü "
            "altında robotik kolları kontrol ettiği ileri bir laparoskopi sistemidir. "
            "Özellikle kompleks endometriozis, miyomektomi (rahim koruyucu myom çıkarma) ve "
            "pelvik prolapsus onarımlarında üstünlük sağlar.</p>"
            "<p><strong>Avantajlar:</strong> daha hassas dikiş, derin anatomik bölgelerde "
            "ulaşılabilirlik, cerrah el titremesinin filtrelenmesi.</p>"

            "<h3>vNOTES — İzsiz Vajinal Cerrahi</h3>"
            "<p>vNOTES, karın duvarına hiç kesi açmadan vajinadan ulaşılarak yapılan en modern "
            "minimal invaziv tekniktir. Uygun hasta seçiminde histerektomi, kist alınması ve "
            "prolapsus onarımı gibi işlemler 'izsiz' şekilde gerçekleştirilir.</p>"
            "<p><strong>Avantajlar:</strong> karın duvarında hiç iz yok, çok düşük postoperatif "
            "ağrı, hızlı mobilizasyon.</p>"

            "<h3>Hangi Teknik Benim İçin Uygun?</h3>"
            "<p>Her üç teknik de güvenlidir, ancak uygun teknik seçimi hastanın anatomisine, "
            "hastalığın yaygınlığına, geçmiş cerrahi öyküsüne ve cerrahın deneyimine bağlıdır. "
            "Ameliyat öncesi değerlendirmede hangi yaklaşımın sizin için ideal olduğunu "
            "ayrıntılı konuşuyoruz.</p>"

            "<p><em>Bireysel değerlendirme için randevu alarak muayene olmanız önerilir.</em></p>"
        ),
        "content_en": (
            "<p>The greatest transformation in gynecologic surgery over the past 20 years has "
            "been the rise of minimally invasive techniques. These approaches replace large "
            "incisions with small millimeter-scale ports — or use natural body orifices "
            "altogether.</p>"

            "<h3>Laparoscopy</h3>"
            "<p>Laparoscopic surgery uses 3-4 small 5-10 mm incisions in the abdomen. A high-"
            "definition camera projects the view onto a monitor. Fibroids, cysts, "
            "endometriosis, and hysterectomy can all be performed safely this way.</p>"
            "<p><strong>Benefits:</strong> less pain, short hospital stay (typically one day), "
            "fast recovery (1-2 weeks), small scars.</p>"

            "<h3>Robotic Surgery</h3>"
            "<p>The robotic platform is an advanced laparoscopy system where the surgeon sits at "
            "a console and controls robotic arms under 3D magnified vision. It is particularly "
            "advantageous for complex endometriosis, uterus-preserving myomectomy, and pelvic "
            "prolapse repair.</p>"
            "<p><strong>Benefits:</strong> more precise suturing, access to deep anatomic "
            "regions, filtering of the surgeon's hand tremor.</p>"

            "<h3>vNOTES — Scarless Vaginal Surgery</h3>"
            "<p>vNOTES is the most modern minimally invasive technique — reaching the surgical "
            "target entirely through the vagina without any abdominal incisions. In selected "
            "patients, hysterectomy, adnexal surgery, and prolapse repair can be performed "
            "'scarlessly.'</p>"
            "<p><strong>Benefits:</strong> no abdominal scars, very low postoperative pain, "
            "rapid mobilization.</p>"

            "<h3>Which Technique Is Right for Me?</h3>"
            "<p>All three techniques are safe, but the best choice depends on the patient's "
            "anatomy, disease extent, surgical history, and surgeon experience. We discuss "
            "this in detail during pre-operative evaluation.</p>"

            "<p><em>Schedule a consultation for an individualized assessment.</em></p>"
        ),
        "meta_title_tr": "Minimal İnvaziv Cerrahi — Laparoskopi, Robotik, vNOTES",
        "meta_title_en": "Minimally Invasive Surgery — Laparoscopy, Robotics, vNOTES",
        "meta_description_tr": "Jinekolojik minimal invaziv cerrahi tekniklerinin karşılaştırması: laparoskopi, robotik ve vNOTES.",
        "meta_description_en": "A comparison of minimally invasive gynecologic surgery techniques: laparoscopy, robotics, and vNOTES.",
    },
    {
        "slug": "saglikli-gebelik-icin-ipuclari",
        "category_name": "Gebelik",
        "related_specialty_slug": "gebelik-takibi",
        "read_time_minutes": 4,
        "is_featured": False,
        "title_tr": "Sağlıklı Bir Gebelik İçin Bilinmesi Gerekenler",
        "title_en": "Key Guidance for a Healthy Pregnancy",
        "excerpt_tr": (
            "Beslenme, egzersiz, takvim muayeneleri ve uyarıcı belirtiler — gebelik sürecinde "
            "sizi ve bebeğinizi destekleyecek önemli başlıklar."
        ),
        "excerpt_en": (
            "Nutrition, exercise, scheduled check-ups, and warning signs — the essentials for "
            "supporting yourself and your baby throughout pregnancy."
        ),
        "content_tr": (
            "<p>Sağlıklı bir gebelik; düzenli muayeneler, dengeli beslenme ve farkındalıkla "
            "desteklendiğinde hem anne hem bebek için güvenli bir deneyim olabilir.</p>"

            "<h3>Trimester Trimester Takip</h3>"
            "<ul>"
            "<li><strong>1. Trimester (0-13 hafta):</strong> gebeliğin doğrulanması, kan grubu, "
            "ense saydamlığı taraması ve erken genetik testler.</li>"
            "<li><strong>2. Trimester (14-27 hafta):</strong> detaylı anomali ultrasonu, "
            "gestasyonel diyabet taraması.</li>"
            "<li><strong>3. Trimester (28-40 hafta):</strong> büyüme takibi, doppler ölçümleri, "
            "NST ve doğum planlaması.</li>"
            "</ul>"

            "<h3>Beslenme ve Vitaminler</h3>"
            "<p>Dengeli protein, tam tahıl, taze sebze-meyve ve yeterli sıvı alımı esastır. "
            "Folik asit (en az gebelik öncesi 1 aydan itibaren), demir, D vitamini ve iyot "
            "eksikliklerinin önlenmesi açısından önemlidir. Ne kadar takviye alacağınızı "
            "hekiminizle görüşün.</p>"

            "<h3>Egzersiz</h3>"
            "<p>Düşük riskli gebeliklerde hafif-orta şiddetli aktivite — tempolu yürüyüş, "
            "yüzme, prenatal yoga — hem annenin hem bebeğin sağlığına iyi gelir. Yüksek riskli "
            "durumlarda egzersiz planı mutlaka hekim onayıyla yapılır.</p>"

            "<h3>Hemen Hekime Başvurmanız Gereken Belirtiler</h3>"
            "<ul>"
            "<li>Ağır vajinal kanama</li>"
            "<li>Şiddetli karın veya pelvik ağrı</li>"
            "<li>Yüksek ateş</li>"
            "<li>Bebek hareketlerinde belirgin azalma (3. trimester)</li>"
            "<li>Görme bulanıklığı, şiddetli baş ağrısı, ani el-yüz şişliği</li>"
            "</ul>"

            "<h3>Psikolojik Destek</h3>"
            "<p>Gebelik sürecinde ruhsal dalgalanmalar ve kaygı yaygındır. Yalnız olmadığınızı "
            "bilin — düzenli takibin bir parçası olarak bu konuları da konuşabileceğiniz "
            "bir hekim-hasta ilişkisi kurmak önemlidir.</p>"

            "<p><em>Kişisel takip ve değerlendirme için randevu alabilirsiniz.</em></p>"
        ),
        "content_en": (
            "<p>A healthy pregnancy — supported by regular check-ups, balanced nutrition, and "
            "awareness — can be a safe experience for both mother and baby.</p>"

            "<h3>Trimester-by-Trimester Follow-up</h3>"
            "<ul>"
            "<li><strong>First Trimester (0-13 weeks):</strong> pregnancy confirmation, blood "
            "type, nuchal translucency screening, early genetic testing.</li>"
            "<li><strong>Second Trimester (14-27 weeks):</strong> detailed anomaly ultrasound, "
            "gestational diabetes screening.</li>"
            "<li><strong>Third Trimester (28-40 weeks):</strong> fetal growth monitoring, "
            "Doppler studies, non-stress tests, delivery planning.</li>"
            "</ul>"

            "<h3>Nutrition and Vitamins</h3>"
            "<p>Balanced protein, whole grains, fresh produce, and adequate hydration are "
            "essential. Folic acid (ideally starting at least a month pre-conception), iron, "
            "vitamin D, and iodine help prevent deficiencies. Discuss supplementation with "
            "your doctor.</p>"

            "<h3>Exercise</h3>"
            "<p>In low-risk pregnancies, light-to-moderate activity — brisk walking, swimming, "
            "prenatal yoga — benefits both mother and baby. In higher-risk pregnancies, "
            "exercise plans should always be approved by your physician.</p>"

            "<h3>When to Seek Immediate Care</h3>"
            "<ul>"
            "<li>Heavy vaginal bleeding</li>"
            "<li>Severe abdominal or pelvic pain</li>"
            "<li>High fever</li>"
            "<li>Noticeable decrease in fetal movement (third trimester)</li>"
            "<li>Blurred vision, severe headache, sudden facial/hand swelling</li>"
            "</ul>"

            "<h3>Emotional Support</h3>"
            "<p>Mood shifts and anxiety during pregnancy are common. You are not alone — "
            "building a relationship with a physician who welcomes these conversations as "
            "part of routine follow-up is important.</p>"

            "<p><em>Schedule an appointment for personalized monitoring.</em></p>"
        ),
        "meta_title_tr": "Sağlıklı Gebelik Rehberi — Dr. Savaş Gündoğan",
        "meta_title_en": "Healthy Pregnancy Guide — Dr. Savaş Gündoğan",
        "meta_description_tr": "Trimester takibi, beslenme, egzersiz ve uyarıcı belirtiler — sağlıklı gebelik için pratik bir rehber.",
        "meta_description_en": "Trimester follow-up, nutrition, exercise, and warning signs — a practical guide to a healthy pregnancy.",
    },
    {
        "slug": "idrar-kacirma-normal-degil",
        "category_name": "Ürojinekoloji",
        "related_specialty_slug": "uroginekoloji",
        "read_time_minutes": 4,
        "is_featured": False,
        "title_tr": "İdrar Kaçırmak 'Normal' Değildir — Modern Tedavi Seçenekleri",
        "title_en": "Urinary Incontinence Is Not 'Normal' — Modern Treatment Options",
        "excerpt_tr": (
            "Öksürünce kaçırmak, ani sıkışma hissi… Pek çok kadının sessizce yaşadığı bu durum "
            "aslında tedavi edilebilir. İşte bilmeniz gerekenler."
        ),
        "excerpt_en": (
            "Leakage with coughing, sudden urgency… Many women live silently with symptoms "
            "that are in fact treatable. Here's what you need to know."
        ),
        "content_tr": (
            "<p>Türkiye'de kadınların yaklaşık üçte biri, hayatlarının bir döneminde idrar "
            "kaçırma sorunu yaşar. Ancak utanma ya da 'bu yaşta normal' düşüncesi nedeniyle "
            "birçoğu hekime başvurmaz. Oysa idrar kaçırmanın nedeni anlaşıldığında, çoğu hasta "
            "cerrahiye gerek kalmadan rahatlama sağlar.</p>"

            "<h3>İki Ana Tip</h3>"
            "<ul>"
            "<li><strong>Stres tipi:</strong> öksürme, hapşırma, gülme, egzersiz sırasında "
            "kaçırma. Pelvik taban kaslarının zayıflığından kaynaklanır.</li>"
            "<li><strong>Sıkışma tipi:</strong> ani ve dayanılmaz idrar yapma hissi. Mesane "
            "kasının aşırı aktif çalışmasıyla ilişkilidir.</li>"
            "<li><strong>Karma tip:</strong> her ikisinin bir arada bulunduğu tablo.</li>"
            "</ul>"

            "<h3>İlk Basamak: Konservatif Tedavi</h3>"
            "<p>Tedaviye her zaman en az invaziv seçenekten başlanır:</p>"
            "<ul>"
            "<li>Pelvik taban fizik tedavisi (Kegel egzersizleri bu kapsamdadır)</li>"
            "<li>Davranışsal düzenlemeler — zamanlı idrar yapma, kafein azaltma, sıvı düzeni</li>"
            "<li>Vajinal pesser uygulaması</li>"
            "<li>Sıkışma tipi için mesane kasını gevşeten ilaçlar</li>"
            "</ul>"

            "<h3>Cerrahi Gerektiğinde</h3>"
            "<p>Konservatif tedaviler yeterli gelmezse modern minimal invaziv cerrahi seçenekler "
            "devreye girer:</p>"
            "<ul>"
            "<li><strong>TVT / TOT sling ameliyatı:</strong> stres tipi idrar kaçırmada idrar "
            "kanalına destek sağlayan 20 dakikalık prosedür.</li>"
            "<li><strong>Sakrokolpopeksi:</strong> ileri evre pelvik organ sarkmalarında "
            "laparoskopik veya robotik onarım.</li>"
            "</ul>"

            "<h3>Neden Sessiz Kalmayın?</h3>"
            "<p>İdrar kaçırma yaşam kalitenizi etkiliyorsa — sosyal yaşamınızı, egzersizinizi, "
            "uykunuzu — bu tedavisi mümkün, yaygın ve konuşulması gereken bir sağlık "
            "sorunudur. İlk muayenenizden sonraki hafta içinde bile fark yaratan adımlar "
            "atılabilir.</p>"

            "<p><em>Değerlendirme için randevu almaktan çekinmeyin.</em></p>"
        ),
        "content_en": (
            "<p>Nearly one in three women in Turkey experiences urinary incontinence at some "
            "point. Yet many avoid seeing a doctor because of embarrassment or the belief "
            "that it is 'normal at this age.' In reality, once the cause is identified, most "
            "patients find relief without surgery.</p>"

            "<h3>Two Main Types</h3>"
            "<ul>"
            "<li><strong>Stress incontinence:</strong> leakage with coughing, sneezing, "
            "laughing, or exercise. Caused by weakened pelvic floor muscles.</li>"
            "<li><strong>Urge incontinence:</strong> sudden, overwhelming urge to urinate. "
            "Linked to overactive bladder muscle contractions.</li>"
            "<li><strong>Mixed type:</strong> features of both.</li>"
            "</ul>"

            "<h3>First Line: Conservative Treatment</h3>"
            "<p>Treatment always begins with the least invasive options:</p>"
            "<ul>"
            "<li>Pelvic floor physiotherapy (Kegel exercises fall within this)</li>"
            "<li>Behavioral adjustments — timed voiding, reducing caffeine, hydration pacing</li>"
            "<li>Vaginal pessary fitting</li>"
            "<li>For urge-type, medications that relax the bladder muscle</li>"
            "</ul>"

            "<h3>When Surgery Is Needed</h3>"
            "<p>If conservative treatments are insufficient, modern minimally invasive surgical "
            "options are available:</p>"
            "<ul>"
            "<li><strong>TVT / TOT sling procedure:</strong> a 20-minute procedure supporting "
            "the urethra in stress incontinence.</li>"
            "<li><strong>Sacrocolpopexy:</strong> laparoscopic or robotic repair for advanced "
            "pelvic organ prolapse.</li>"
            "</ul>"

            "<h3>Why You Should Not Stay Silent</h3>"
            "<p>If incontinence is affecting your quality of life — your social life, exercise, "
            "or sleep — this is a treatable, common, and deserving-to-be-discussed health "
            "issue. Even within a week of your first consultation, meaningful steps can be "
            "taken.</p>"

            "<p><em>Don't hesitate to schedule an evaluation.</em></p>"
        ),
        "meta_title_tr": "İdrar Kaçırma Tedavisi — Ürojinekoloji",
        "meta_title_en": "Urinary Incontinence Treatment — Urogynecology",
        "meta_description_tr": "Stres ve sıkışma tipi idrar kaçırmada modern tedavi seçenekleri. Konservatif yöntemler ve cerrahi.",
        "meta_description_en": "Modern treatment options for stress and urge urinary incontinence. Conservative methods and surgery.",
    },
    {
        "slug": "jinekolojik-tarama-neden-onemli",
        "category_name": "Koruyucu Jinekoloji",
        "related_specialty_slug": "jinekolojik-onkoloji",
        "read_time_minutes": 4,
        "is_featured": False,
        "title_tr": "Yıllık Jinekolojik Tarama Neden Hayat Kurtarır?",
        "title_en": "Why Annual Gynecologic Screening Saves Lives",
        "excerpt_tr": (
            "HPV, smear ve ultrason kombinasyonu — rahim ağzı ve yumurtalık kanserleri gibi "
            "ciddi hastalıkların erken yakalanmasında altın standart."
        ),
        "excerpt_en": (
            "HPV testing, Pap smear, and ultrasound — the combination that forms the gold "
            "standard for early detection of cervical and ovarian cancers."
        ),
        "content_tr": (
            "<p>Jinekolojik kanserlerin erken tanısı, sağ kalım oranlarını dramatik biçimde "
            "artırır. Erken evrede yakalanan rahim ağzı kanserinde 5 yıllık sağ kalım %92 "
            "civarındayken, ileri evrede bu oran %17'ye düşer. Bu fark, rutin taramaların "
            "neden bu kadar önemli olduğunu gösterir.</p>"

            "<h3>Hangi Tarama Ne Zaman?</h3>"
            "<ul>"
            "<li><strong>25 yaş altı:</strong> HPV aşısı tamamlanmamışsa yapılmalı. Tarama "
            "genellikle aktif cinsel yaşam başladıktan 3-5 yıl sonra başlar.</li>"
            "<li><strong>25-30 yaş:</strong> 3 yılda bir smear.</li>"
            "<li><strong>30-65 yaş:</strong> 5 yılda bir HPV + smear (ko-testing) veya 3 yılda "
            "bir tek başına smear.</li>"
            "<li><strong>65 yaş üzeri:</strong> önceki düzenli taramalar negatifse tarama "
            "sonlandırılabilir. Aksi durumda sürdürülür.</li>"
            "</ul>"

            "<h3>Pelvik Ultrason</h3>"
            "<p>Yıllık veya risk durumuna göre daha sık yapılan transvajinal ultrason; "
            "yumurtalık kistleri, myomlar ve endometriyum değişikliklerinin erken saptanmasını "
            "sağlar. Özellikle ailesinde over kanseri öyküsü olan kadınlarda atlanmamalıdır.</p>"

            "<h3>HPV Aşısı</h3>"
            "<p>HPV aşısı, rahim ağzı kanserine neden olan virüs tiplerine karşı etkili "
            "korunma sağlar. 9-26 yaş aralığında aşılama ideal kabul edilir, ancak 45 yaşına "
            "kadar da fayda sağlayabilir. Aşı, mevcut enfeksiyonları tedavi etmez; bu nedenle "
            "taramaları ikame etmez.</p>"

            "<h3>Genetik Risk</h3>"
            "<p>Ailede meme veya yumurtalık kanseri öyküsü varsa BRCA1/BRCA2 gen mutasyonu "
            "araştırılmalıdır. Genetik testler, tarama protokolünü ve koruyucu cerrahi "
            "kararlarını şekillendirir.</p>"

            "<h3>Sonuç</h3>"
            "<p>Tarama, kanseri önlemez — ancak erken yakalar. Erken yakalanan hastalık, "
            "modern cerrahi ve tedavilerle büyük ölçüde yönetilebilir. Yıllık muayeneyi "
            "ertelemeyin.</p>"

            "<p><em>Tarama takvimi için randevu alabilirsiniz.</em></p>"
        ),
        "content_en": (
            "<p>Early detection of gynecologic cancers dramatically improves survival. For "
            "cervical cancer, the 5-year survival is around 92% when caught early — but "
            "falls to roughly 17% at advanced stages. This difference highlights why routine "
            "screening matters so much.</p>"

            "<h3>Which Screening, When?</h3>"
            "<ul>"
            "<li><strong>Under 25:</strong> HPV vaccination should be completed if not yet "
            "done. Screening typically begins 3-5 years after initiation of sexual activity.</li>"
            "<li><strong>25-30 years:</strong> Pap smear every 3 years.</li>"
            "<li><strong>30-65 years:</strong> co-testing (HPV + Pap) every 5 years, or Pap "
            "alone every 3 years.</li>"
            "<li><strong>Over 65:</strong> if prior screenings were consistently negative, "
            "screening may be discontinued. Otherwise continued.</li>"
            "</ul>"

            "<h3>Pelvic Ultrasound</h3>"
            "<p>Annual or risk-adjusted transvaginal ultrasound helps detect ovarian cysts, "
            "fibroids, and endometrial changes early. It should not be skipped — particularly "
            "in women with a family history of ovarian cancer.</p>"

            "<h3>HPV Vaccination</h3>"
            "<p>The HPV vaccine provides effective protection against the virus types that "
            "cause cervical cancer. Ages 9-26 are ideal, though benefit extends to age 45. "
            "The vaccine does not treat existing infections — it does not replace screening.</p>"

            "<h3>Genetic Risk</h3>"
            "<p>Where there is a family history of breast or ovarian cancer, BRCA1/BRCA2 "
            "genetic testing should be considered. Results guide both surveillance "
            "protocols and decisions about risk-reducing surgery.</p>"

            "<h3>Conclusion</h3>"
            "<p>Screening does not prevent cancer — but it catches it early. Early-stage "
            "disease can be substantially managed with modern surgery and therapies. Do "
            "not postpone your annual examination.</p>"

            "<p><em>Schedule an appointment to plan your screening calendar.</em></p>"
        ),
        "meta_title_tr": "Yıllık Jinekolojik Tarama Rehberi",
        "meta_title_en": "Annual Gynecologic Screening Guide",
        "meta_description_tr": "Smear, HPV testi ve pelvik ultrason — yaşa göre tarama takvimi ve erken tanının değeri.",
        "meta_description_en": "Pap smear, HPV testing, and pelvic ultrasound — age-based screening schedule and the value of early detection.",
    },
]


# =====================================================================
# Additional FAQ items
# =====================================================================
EXTRA_FAQS = [
    {
        "question_tr": "Randevu öncesi hangi bilgileri hazırlamalıyım?",
        "question_en": "What information should I prepare before my appointment?",
        "answer_tr": (
            "<p>Muayene verimliliği için şu bilgileri hazırlamanızı öneririm: adet "
            "düzeniniz ve son adet tarihiniz, kullandığınız ilaçlar ve varsa bilinen "
            "alerjiler, ailede meme/yumurtalık kanseri öyküsü, önceki ameliyat raporları "
            "ve mevcut kan tahlilleri. Mevcut görüntüleme raporları varsa (ultrason, "
            "MR) birlikte getirin.</p>"
        ),
        "answer_en": (
            "<p>To make your visit productive, please bring: your menstrual pattern and "
            "last period date, current medications and known allergies, family history "
            "of breast or ovarian cancer, prior operative reports, and recent blood "
            "work. Any imaging reports (ultrasound, MRI) should come with you.</p>"
        ),
        "is_featured": True,
    },
    {
        "question_tr": "Robotik cerrahi ile laparoskopi arasındaki fark nedir?",
        "question_en": "What is the difference between robotic surgery and laparoscopy?",
        "answer_tr": (
            "<p>İkisi de minimal invaziv (küçük kesili) cerrahi yaklaşımlardır. Robotik "
            "cerrahide cerrah konsolda oturarak 3 boyutlu görüntü altında çalışır ve "
            "robotik kolların geniş hareket kabiliyeti kompleks dikişlerde avantaj "
            "sağlar. Laparoskopi standart ve her merkezde mevcut olan güvenli bir "
            "tekniktir. Her vakada hangi yaklaşımın uygun olduğunu anatomi ve cerrahi "
            "hedefe göre birlikte belirliyoruz.</p>"
        ),
        "answer_en": (
            "<p>Both are minimally invasive (small-incision) approaches. In robotic "
            "surgery the surgeon operates from a console with 3D vision and the "
            "robotic arms' broad range of motion is advantageous for complex "
            "suturing. Laparoscopy is a standard, widely available, safe technique. "
            "Which approach best fits each case depends on anatomy and the surgical "
            "goal — we decide this together.</p>"
        ),
        "is_featured": False,
    },
    {
        "question_tr": "HPV aşısını hangi yaşta yaptırmalıyım?",
        "question_en": "At what age should I get the HPV vaccine?",
        "answer_tr": (
            "<p>HPV aşısı için ideal yaş aralığı 9-26'dır, ancak 45 yaşına kadar da "
            "fayda sağlayabilir. Cinsel aktivite başlamadan önce yapılan aşılama en "
            "etkili koruma sağlar. Aşı, mevcut HPV enfeksiyonlarını tedavi etmez — bu "
            "nedenle aşı olsanız bile rutin smear taramasına devam etmeniz gerekir.</p>"
        ),
        "answer_en": (
            "<p>The ideal window for HPV vaccination is ages 9-26, though benefits "
            "extend up to age 45. Vaccination before the onset of sexual activity "
            "provides the strongest protection. The vaccine does not treat existing "
            "HPV infections, so routine Pap smear screening should continue even "
            "after vaccination.</p>"
        ),
        "is_featured": False,
    },
    {
        "question_tr": "Menopoza ne zaman girdiğimi nasıl anlarım?",
        "question_en": "How do I know when I have entered menopause?",
        "answer_tr": (
            "<p>Menopoz, ardışık 12 ay adet görmeme durumu ile tanımlanır. Ortalama "
            "başlangıç yaşı 48-52 arasındadır. Menopoza geçiş döneminde (perimenopoz) "
            "düzensiz adetler, ateş basmaları, uyku bozuklukları ve ruh hali "
            "değişiklikleri görülebilir. Kesin tanı için hormon seviyeleri ve klinik "
            "tablo birlikte değerlendirilir.</p>"
        ),
        "answer_en": (
            "<p>Menopause is defined as 12 consecutive months without a period. The "
            "average age of onset is between 48 and 52. During the transition "
            "(perimenopause), you may experience irregular cycles, hot flashes, "
            "sleep disturbances, and mood changes. A definitive diagnosis combines "
            "hormone levels with the clinical picture.</p>"
        ),
        "is_featured": True,
    },
    {
        "question_tr": "Gebelik planlıyorsam önceden hangi kontrolleri yaptırmalıyım?",
        "question_en": "What pre-conception check-ups are recommended?",
        "answer_tr": (
            "<p>Gebelik planlamadan önceki 2-3 ay içinde şu kontroller önerilir: "
            "jinekolojik muayene ve pelvik ultrason, hemogram, kan grubu, hepatit B "
            "ve C, HIV, tiroid fonksiyonları, D vitamini, kızamıkçık/suçiçeği "
            "bağışıklığı. Folik asit takviyesine en az 1 ay önceden başlanmalıdır. "
            "Kronik hastalıkları olan kadınlarda (diyabet, tiroid, hipertansiyon) "
            "multidisipliner değerlendirme yapılır.</p>"
        ),
        "answer_en": (
            "<p>Ideally 2-3 months before attempting pregnancy, the following are "
            "recommended: gynecologic exam and pelvic ultrasound, CBC, blood type, "
            "hepatitis B and C, HIV, thyroid panel, vitamin D, and rubella/varicella "
            "immunity. Folic acid supplementation should begin at least one month "
            "prior. Women with chronic conditions (diabetes, thyroid disease, "
            "hypertension) benefit from multidisciplinary preconception care.</p>"
        ),
        "is_featured": False,
    },
]


class Command(BaseCommand):
    help = "Phase 2 content fill — video, blog posts, additional FAQs."

    @transaction.atomic
    def handle(self, *args, **opts):
        self._add_video()
        self._add_blog_posts()
        self._add_faqs()
        self.stdout.write(self.style.SUCCESS("\nPhase 2 content fill done."))

    # ------------------------------------------------------------------
    def _add_video(self):
        url = YOUTUBE_VIDEO["video_url"]
        if Video.objects.filter(video_url=url).exists():
            self.stdout.write(f"  [=] Video already exists: {url}")
            return
        # Ensure category exists
        cat, _ = VideoCategory.objects.get_or_create(
            slug="menopoz", defaults={"name": "Menopoz", "order": 10}
        )
        v = Video(
            title_tr=YOUTUBE_VIDEO["title_tr"],
            title_en=YOUTUBE_VIDEO["title_en"],
            description_tr=YOUTUBE_VIDEO["description_tr"],
            description_en=YOUTUBE_VIDEO["description_en"],
            platform=YOUTUBE_VIDEO["platform"],
            video_url=url,
            category=cat,
            is_featured=YOUTUBE_VIDEO["is_featured"],
            is_official_acibadem=YOUTUBE_VIDEO["is_official_acibadem"],
            publish_date=timezone.now().date(),
            order=0,
        )
        v.save()
        self.stdout.write(self.style.SUCCESS(f"  [ok] Video added: {YOUTUBE_VIDEO['title_tr']}"))

    # ------------------------------------------------------------------
    def _add_blog_posts(self):
        for data in BLOG_POSTS:
            if BlogPost.objects.filter(slug=data["slug"]).exists():
                self.stdout.write(f"  [=] BlogPost '{data['slug']}' already exists")
                continue
            cat, _ = BlogCategory.objects.get_or_create(
                slug=data["category_name"].lower().replace(" ", "-").replace("ı", "i"),
                defaults={"name": data["category_name"]},
            )
            specialty = SpecialtyArea.objects.filter(slug=data["related_specialty_slug"]).first()
            post = BlogPost(
                slug=data["slug"],
                title_tr=data["title_tr"],
                title_en=data["title_en"],
                excerpt_tr=data["excerpt_tr"],
                excerpt_en=data["excerpt_en"],
                content_tr=data["content_tr"],
                content_en=data["content_en"],
                meta_title_tr=data["meta_title_tr"],
                meta_title_en=data["meta_title_en"],
                meta_description_tr=data["meta_description_tr"],
                meta_description_en=data["meta_description_en"],
                category=cat,
                related_specialty=specialty,
                read_time_minutes=data["read_time_minutes"],
                is_featured=data["is_featured"],
                status="published",
                published_at=timezone.now(),
            )
            post.save()
            self.stdout.write(self.style.SUCCESS(f"  [ok] BlogPost '{data['slug']}' created"))

    # ------------------------------------------------------------------
    def _add_faqs(self):
        cat, _ = FAQCategory.objects.get_or_create(
            name_tr="Genel Sorular", defaults={"name_en": "General", "order": 0}
        )
        for q in EXTRA_FAQS:
            if FAQItem.objects.filter(question_tr=q["question_tr"]).exists():
                continue
            FAQItem.objects.create(
                question_tr=q["question_tr"],
                question_en=q["question_en"],
                answer_tr=q["answer_tr"],
                answer_en=q["answer_en"],
                is_featured=q["is_featured"],
                category=cat,
            )
            self.stdout.write(self.style.SUCCESS(f"  [ok] FAQ added: {q['question_tr'][:50]}"))
