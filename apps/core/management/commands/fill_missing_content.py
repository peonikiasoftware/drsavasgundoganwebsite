"""Fill empty/missing content across all models with professional TR+EN copy.

Idempotent — only writes to fields that are currently empty. Safe to re-run.
The doctor can edit anything the command populated via /doctor-admin/.

Run:
    python manage.py fill_missing_content
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.models import SiteSettings
from apps.experience.models import Education, Experience
from apps.expertise.models import SpecialtyArea


def _is_empty(val) -> bool:
    if val is None:
        return True
    s = str(val).strip()
    return s in ("", "<p>&nbsp;</p>", "<p></p>")


def _set_if_empty(obj, field: str, value: str) -> bool:
    if _is_empty(getattr(obj, field, None)):
        setattr(obj, field, value)
        return True
    return False


# =====================================================================
# SPECIALTY AREA CONTENT (TR + EN)
# =====================================================================
SPECIALTY_CONTENT = {
    # --------------------------------------------------------------
    "endometriozis": {
        "full_description_tr": (
            "<p>Endometriozis, rahim iç dokusunun (endometrium) rahim dışındaki organlarda "
            "yerleşerek büyümesiyle ortaya çıkan kronik bir hastalıktır. Her ay adet "
            "döngüsüne eşlik eden bu ektopik dokular kanar, iltihaplanır ve zamanla "
            "yapışıklıklara yol açarak hem yaşam kalitesini hem de doğurganlığı "
            "olumsuz etkileyebilir.</p>"
            "<p>Kliniğimde endometriozisi yalnızca bir ağrı sorunu olarak değil, "
            "hastanın yaşamını kuşatan çok katmanlı bir süreç olarak ele alıyorum. "
            "Tanıdan cerrahi tedaviye, hormonal yönetimden doğurganlık planlamasına "
            "kadar her adımda bütüncül bir yaklaşım benimsiyorum.</p>"
        ),
        "full_description_en": (
            "<p>Endometriosis is a chronic condition in which tissue similar to the uterine "
            "lining grows outside the uterus — on the ovaries, fallopian tubes, bowel, "
            "or bladder. These ectopic tissues bleed and inflame with every menstrual "
            "cycle, gradually forming adhesions that compromise both quality of life "
            "and fertility.</p>"
            "<p>In my practice, I treat endometriosis not merely as a pain problem "
            "but as a multi-layered process that affects the whole patient — from "
            "diagnosis and surgical treatment to hormonal management and fertility "
            "planning.</p>"
        ),
        "symptoms_tr": (
            "<p>Endometriozisin belirtileri kişiden kişiye büyük farklılık gösterir. "
            "Bazı hastalarda hafif regl ağrısı olarak başlayan şikâyet, yıllar içinde "
            "günlük yaşamı kısıtlayan bir tabloya dönüşebilir.</p>"
            "<ul>"
            "<li>Şiddetli ve yıllar içinde artan adet ağrısı (dismenore)</li>"
            "<li>Cinsel ilişki sırasında derin ağrı (disparöni)</li>"
            "<li>Kronik pelvik ağrı — adet dönemi dışında da devam eden</li>"
            "<li>Tuvalete çıkarken ağrı, özellikle adet döneminde</li>"
            "<li>Yorgunluk, bulantı, şişkinlik ve bağırsak düzensizlikleri</li>"
            "<li>Bir yıldan uzun süren korunmasız ilişkiye rağmen gebelik sağlanamaması</li>"
            "</ul>"
        ),
        "symptoms_en": (
            "<p>Symptoms vary widely from patient to patient. What begins as mild "
            "menstrual discomfort can, over years, evolve into a condition that "
            "restricts daily life.</p>"
            "<ul>"
            "<li>Severe and progressively worsening menstrual pain (dysmenorrhea)</li>"
            "<li>Deep pain during intercourse (dyspareunia)</li>"
            "<li>Chronic pelvic pain persisting outside of menstruation</li>"
            "<li>Painful urination or bowel movements, especially during periods</li>"
            "<li>Fatigue, nausea, bloating, and gastrointestinal irregularity</li>"
            "<li>Difficulty conceiving after a year of unprotected intercourse</li>"
            "</ul>"
        ),
        "treatment_approach_tr": (
            "<p>Tedavi planını hiçbir zaman tek başına belirtilere değil, hastanın yaşı, "
            "çocuk sahibi olma isteği, hastalığın evresi ve günlük yaşamına etkisine göre "
            "şekillendiriyorum. Gerektiğinde hormonal tedavi, ağrı yönetimi ve cerrahi "
            "seçenekleri bir arada değerlendiriyorum.</p>"
            "<p>Cerrahi gerektiğinde tercihim minimal invaziv tekniklerdir: "
            "laparoskopi, robotik cerrahi ve seçilmiş olgularda vNOTES (izsiz vajinal "
            "cerrahi). Bu tekniklerle endometriotik odaklar ve yapışıklıklar yüksek "
            "büyütme altında hassasiyetle temizlenir, yumurtalık rezervi korunur, "
            "iyileşme süresi kısalır.</p>"
        ),
        "treatment_approach_en": (
            "<p>I never design a treatment plan around symptoms alone. The patient's "
            "age, fertility goals, disease stage, and impact on daily life all guide "
            "our decision — hormonal therapy, pain management, and surgery are "
            "weighed together.</p>"
            "<p>When surgery is indicated, I favor minimally invasive techniques: "
            "laparoscopy, robotic surgery, and in selected cases vNOTES (scarless "
            "vaginal surgery). These approaches allow precise removal of "
            "endometriotic foci and adhesions under magnification, preservation of "
            "ovarian reserve, and a faster recovery.</p>"
        ),
        "recovery_info_tr": (
            "<p>Minimal invaziv endometriozis cerrahisi sonrası hastaların büyük çoğunluğu "
            "aynı gün veya bir gece hastanede kaldıktan sonra taburcu olur. Hafif işlere "
            "3-5 gün içinde, yoğun fiziksel aktiviteye ise genellikle 2-3 hafta içinde "
            "dönülür.</p>"
            "<p>Ameliyat sonrası ilk 3 ay kritik takip dönemidir. Bu süreçte ağrı "
            "kontrolü, hormonal yönetim ve gerektiğinde doğurganlık planlaması birlikte "
            "yürütülür. Hastalığın nüks etme ihtimaline karşı uzun dönemli izlem "
            "planlıyorum.</p>"
        ),
        "recovery_info_en": (
            "<p>After minimally invasive endometriosis surgery, most patients are "
            "discharged the same day or after one overnight stay. Light activity "
            "resumes within 3-5 days; full physical exertion is usually possible "
            "within 2-3 weeks.</p>"
            "<p>The first 3 months post-surgery are a critical follow-up window. "
            "Pain control, hormonal management, and — where relevant — fertility "
            "planning are coordinated together. I maintain long-term surveillance "
            "because recurrence is possible.</p>"
        ),
        "meta_title_tr": "Endometriozis Tedavisi — Op. Dr. Savaş Gündoğan",
        "meta_title_en": "Endometriosis Treatment — M.D. Savaş Gündoğan",
        "meta_description_tr": (
            "Endometriozis tanı, hormonal tedavi ve minimal invaziv cerrahi. "
            "Laparoskopi ve vNOTES ile ağrı kontrolü ve doğurganlığın korunması. "
            "Acıbadem Maslak."
        ),
        "meta_description_en": (
            "Endometriosis diagnosis, hormonal therapy, and minimally invasive "
            "surgery. Pain control and fertility preservation via laparoscopy and "
            "vNOTES. Acıbadem Maslak."
        ),
    },

    # --------------------------------------------------------------
    "laparoskopik-cerrahi": {
        "symptoms_tr": (
            "<p>Laparoskopik cerrahi, bir belirti değil bir tedavi yöntemidir. Şu durumlarda "
            "tercih edilir:</p>"
            "<ul>"
            "<li>Myom (rahim leiomyomu) — menoraji, bası, infertilite şikâyeti yapanlar</li>"
            "<li>Yumurtalık kistleri ve kitle taramalarında şüpheli bulgular</li>"
            "<li>Endometriozis — özellikle derin infiltratif formlar</li>"
            "<li>Rahim dışı gebelik (ektopik gebelik)</li>"
            "<li>Pelvik yapışıklıklar ve kronik pelvik ağrı</li>"
            "<li>Tanı amaçlı pelvik değerlendirme (diyagnostik laparoskopi)</li>"
            "</ul>"
        ),
        "symptoms_en": (
            "<p>Laparoscopic surgery is not a symptom but a treatment modality. "
            "It is preferred in the following conditions:</p>"
            "<ul>"
            "<li>Uterine fibroids (leiomyomas) causing menorrhagia, pressure, or infertility</li>"
            "<li>Ovarian cysts or suspicious adnexal masses</li>"
            "<li>Endometriosis — particularly deep infiltrating disease</li>"
            "<li>Ectopic (tubal) pregnancy</li>"
            "<li>Pelvic adhesions and chronic pelvic pain</li>"
            "<li>Diagnostic pelvic evaluation (diagnostic laparoscopy)</li>"
            "</ul>"
        ),
        "treatment_approach_tr": (
            "<p>Laparoskopik cerrahi, karnın birkaç küçük kesiden (5-10 mm) yüksek "
            "çözünürlüklü kamera ve ince cerrahi aletlerle girilmesi esasına dayanır. "
            "Açık cerrahiye kıyasla daha az kanama, daha az ağrı, daha kısa hastanede "
            "kalış ve estetik açıdan çok daha iyi sonuçlar sağlar.</p>"
            "<p>İtalya'da Università degli Studi dell'Insubria bünyesindeki minimal "
            "invaziv cerrahi eğitimim ve yıllardır sürdürdüğüm yüksek hacimli pratiğim "
            "sayesinde kompleks olgularda bile — büyük myomlar, ileri evre endometriozis, "
            "geçirilmiş ameliyat öyküsü — laparoskopik yaklaşımı güvenle uyguluyorum.</p>"
        ),
        "treatment_approach_en": (
            "<p>Laparoscopic surgery is performed through a few small incisions "
            "(5-10 mm) using a high-definition camera and fine surgical instruments. "
            "Compared with open surgery, it offers less bleeding, less pain, a shorter "
            "hospital stay, and superior aesthetic outcomes.</p>"
            "<p>My fellowship in minimally invasive surgery at Università degli "
            "Studi dell'Insubria (Italy), together with years of high-volume practice, "
            "allows me to apply laparoscopy confidently even in complex cases — "
            "large fibroids, advanced endometriosis, and patients with prior surgery.</p>"
        ),
        "recovery_info_tr": (
            "<p>Laparoskopik işlem sonrası hastalar genellikle aynı gün veya ertesi gün "
            "taburcu olur. İlk 24-48 saatte hafif omuz ağrısı (karın içi gaz nedeniyle) "
            "görülebilir, bu beklenen bir durumdur ve kısa sürede geçer.</p>"
            "<p>Hafif yürüyüş ilk günden başlar. Banyo 2-3 gün içinde yapılabilir. "
            "Masa başı işlere 5-7 gün, ağır fiziksel aktivitelere 2-4 hafta içinde "
            "dönülür. Kontrol muayeneleri 10. gün ve 6. hafta olarak planlanır.</p>"
        ),
        "recovery_info_en": (
            "<p>Most patients are discharged the same day or the next morning after "
            "laparoscopy. Mild shoulder discomfort during the first 24-48 hours "
            "(from residual abdominal gas) is expected and resolves quickly.</p>"
            "<p>Light walking begins on day one. Showering is usually permitted "
            "within 2-3 days. Desk work resumes in 5-7 days; vigorous activity "
            "in 2-4 weeks. Follow-up visits are scheduled at day 10 and week 6.</p>"
        ),
        "meta_title_tr": "Laparoskopik Cerrahi — Op. Dr. Savaş Gündoğan",
        "meta_title_en": "Laparoscopic Surgery — M.D. Savaş Gündoğan",
        "meta_description_tr": (
            "Jinekolojik laparoskopik cerrahi: myom, kist, endometriozis ve daha fazlası. "
            "Minimal invaziv teknikle hızlı iyileşme, minimum iz. Acıbadem Maslak."
        ),
        "meta_description_en": (
            "Gynecologic laparoscopic surgery — fibroids, cysts, endometriosis and "
            "more. Faster recovery and minimal scarring. Acıbadem Maslak."
        ),
    },

    # --------------------------------------------------------------
    "robotik-cerrahi": {
        "full_description_tr": (
            "<p>Robotik cerrahi, laparoskopik cerrahinin bir üst basamağı olarak kabul "
            "edilir. Cerrah, konsol başında oturup üç boyutlu ve yüksek büyütmeli bir "
            "görüntü altında robotik kolları kontrol eder. Aletlerin insan bileğinden "
            "çok daha geniş hareket kabiliyeti (EndoWrist), cerrahın el titremesinin "
            "sıfırlanması ve süper hassas dikiş imkânı bu tekniği özellikle karmaşık "
            "vakalarda üstün kılar.</p>"
            "<p>Kliniğimde robotik platform başta myomektomi (çocuk isteyen hastalarda "
            "rahim koruyucu myom çıkarma), derin infiltratif endometriozis ve seçilmiş "
            "histerektomi vakaları için tercih edilir.</p>"
        ),
        "full_description_en": (
            "<p>Robotic surgery is the next evolution of laparoscopy. The surgeon sits "
            "at a console, viewing the operative field in three-dimensional high "
            "magnification, and controls robotic arms whose wristed instruments "
            "(EndoWrist) articulate far beyond the human wrist. Tremor filtration "
            "and superior suturing precision make it especially valuable in complex "
            "cases.</p>"
            "<p>In my practice, the robotic platform is my preferred approach for "
            "myomectomy (uterus-preserving fibroid removal in women desiring "
            "fertility), deep infiltrating endometriosis, and selected hysterectomy "
            "cases.</p>"
        ),
        "symptoms_tr": (
            "<p>Robotik cerrahi, şu klinik durumlarda özellikle avantaj sağlar:</p>"
            "<ul>"
            "<li>Çok sayıda veya derin yerleşimli myomlarda rahim koruyucu miyomektomi</li>"
            "<li>Derin infiltratif endometriozis (bağırsak, mesane, uterosakral tutulumları)</li>"
            "<li>Yapışıklık öyküsü olan kompleks olgularda histerektomi</li>"
            "<li>Pelvik organ prolapsusu için sakrokolpopeksi</li>"
            "<li>Erken evre jinekolojik onkolojik vakalarda evreleme cerrahisi</li>"
            "</ul>"
        ),
        "symptoms_en": (
            "<p>Robotic surgery is particularly advantageous in the following "
            "clinical scenarios:</p>"
            "<ul>"
            "<li>Uterus-preserving myomectomy for multiple or deeply located fibroids</li>"
            "<li>Deep infiltrating endometriosis (bowel, bladder, uterosacral)</li>"
            "<li>Complex hysterectomy in patients with extensive adhesions</li>"
            "<li>Sacrocolpopexy for pelvic organ prolapse</li>"
            "<li>Staging surgery for early-stage gynecologic cancers</li>"
            "</ul>"
        ),
        "treatment_approach_tr": (
            "<p>Her hastanın anatomisi, hastalığın özellikleri ve beklentileri "
            "farklıdır. Robotik yaklaşımı seçmeden önce hasta ile birlikte tüm "
            "cerrahi seçenekleri — laparoskopi, robotik, vNOTES ve gereğinde açık "
            "cerrahi — detaylıca konuşuyorum. Hangi tekniğin seçileceğini hastalığın "
            "yaygınlığı, geçmiş ameliyat öyküsü ve cerrahi sürenin tahmini belirler.</p>"
            "<p>Robotik sistemin sunduğu hassasiyet sayesinde özellikle uterusu "
            "koruyarak myom çıkarma operasyonlarında kas tabakasını çok katmanlı "
            "ve ince dikişlerle rekonstrükte edebiliyorum — bu sonraki gebeliklerde "
            "rahim duvarının bütünlüğü açısından kritiktir.</p>"
        ),
        "treatment_approach_en": (
            "<p>Every patient's anatomy, disease pattern, and expectations are "
            "unique. Before choosing the robotic approach, I discuss all surgical "
            "options with the patient — laparoscopy, robotics, vNOTES, and, when "
            "needed, open surgery. The choice depends on disease extent, prior "
            "surgical history, and estimated operative time.</p>"
            "<p>The precision of the robotic platform is particularly valuable "
            "for uterus-preserving myomectomy, where I can reconstruct the "
            "myometrium in multiple fine suture layers — crucial for uterine wall "
            "integrity in future pregnancies.</p>"
        ),
        "recovery_info_tr": (
            "<p>Robotik cerrahi sonrası hastanede kalış süresi genellikle 1-2 gündür. "
            "Ağrı kontrolü, laparoskopiye benzer şekilde oral ağrı kesicilerle "
            "sağlanabilir. Günlük yaşama dönüş 1-2 hafta içinde mümkündür.</p>"
            "<p>Myomektomi sonrası gebelik planlayan hastalara dikiş iyileşmesinin "
            "tamamlanması için genellikle 4-6 ay beklemelerini öneriyorum. Bu süre "
            "her olguda ameliyat bulgularına göre bireysel olarak değerlendirilir.</p>"
        ),
        "recovery_info_en": (
            "<p>Hospital stay after robotic surgery is typically 1-2 days. Pain is "
            "controlled with oral medications, similar to laparoscopy. Return to "
            "daily activities is usually possible within 1-2 weeks.</p>"
            "<p>Patients planning pregnancy after myomectomy are generally advised "
            "to wait 4-6 months for complete suture healing. This interval is "
            "tailored individually based on intraoperative findings.</p>"
        ),
        "meta_title_tr": "Robotik Jinekolojik Cerrahi — Op. Dr. Savaş Gündoğan",
        "meta_title_en": "Robotic Gynecologic Surgery — M.D. Savaş Gündoğan",
        "meta_description_tr": (
            "Robotik myomektomi, endometriozis cerrahisi ve daha fazlası. Üç boyutlu "
            "görüntü ve EndoWrist hassasiyetiyle kompleks vakalarda güvenli cerrahi."
        ),
        "meta_description_en": (
            "Robotic myomectomy, endometriosis surgery, and more — 3D visualization "
            "and EndoWrist precision for safe complex gynecologic surgery."
        ),
    },

    # --------------------------------------------------------------
    "vnotes-izsiz-vajinal-cerrahi": {
        "full_description_tr": (
            "<p>vNOTES (vaginal Natural Orifice Transluminal Endoscopic Surgery), "
            "karında hiç kesi açmadan doğal vücut açıklığı olan vajinadan ulaşılarak "
            "yapılan ileri düzey minimal invaziv cerrahi tekniğidir. Karın duvarında "
            "iz kalmaz, hasta çok daha kısa sürede iyileşir ve ameliyat sonrası ağrı "
            "kayda değer ölçüde azalır.</p>"
            "<p>Türkiye'de vNOTES uygulayabilen sınırlı sayıda cerrahtan biri olarak, "
            "bu tekniği uygun hasta seçimi ve özel eğitim gerektiren bir teknik "
            "olarak titizlikle uyguluyorum.</p>"
        ),
        "full_description_en": (
            "<p>vNOTES (vaginal Natural Orifice Transluminal Endoscopic Surgery) is an "
            "advanced minimally invasive technique performed entirely through the "
            "vagina — a natural body orifice — with no abdominal incisions at all. "
            "There are no scars on the abdominal wall, patients recover faster, and "
            "post-operative pain is significantly reduced.</p>"
            "<p>As one of a limited number of surgeons performing vNOTES in Turkey, "
            "I apply this technique with careful patient selection and the rigor it "
            "demands.</p>"
        ),
        "symptoms_tr": (
            "<p>vNOTES şu girişimler için uygun olabilir:</p>"
            "<ul>"
            "<li>Total histerektomi (rahim alımı) — uygun boyutta rahim için</li>"
            "<li>Adneksiyel cerrahi (yumurtalık kisti, tuba operasyonları)</li>"
            "<li>Salpingo-ooferektomi (tüp ve yumurtalık alınması)</li>"
            "<li>Pelvik organ prolapsusu onarımı</li>"
            "<li>Tüp ligasyonu (kalıcı gebelik önleme)</li>"
            "</ul>"
            "<p>Tekniğin uygunluğu her hasta için bireysel olarak değerlendirilir — "
            "önceki pelvik cerrahi öyküsü, endometriozis yaygınlığı ve anatomik "
            "faktörler belirleyicidir.</p>"
        ),
        "symptoms_en": (
            "<p>vNOTES may be suitable for the following procedures:</p>"
            "<ul>"
            "<li>Total hysterectomy — for appropriately sized uteri</li>"
            "<li>Adnexal surgery (ovarian cysts, tubal procedures)</li>"
            "<li>Salpingo-oophorectomy (tube and ovary removal)</li>"
            "<li>Pelvic organ prolapse repair</li>"
            "<li>Tubal ligation (permanent contraception)</li>"
            "</ul>"
            "<p>Suitability is assessed individually — prior pelvic surgery, extent "
            "of endometriosis, and anatomic factors all matter.</p>"
        ),
        "treatment_approach_tr": (
            "<p>vNOTES uygulanabilmesi için hastanın anatomik olarak uygun olması, "
            "rahim boyutunun belirli sınırlar içinde olması ve geçmiş pelvik cerrahi "
            "öyküsünün değerlendirilmesi gerekir. Her hastayı ameliyat öncesi "
            "ayrıntılı muayene ve görüntüleme ile değerlendiriyorum.</p>"
            "<p>Tekniği güvenli kılan şey cerrahi deneyim kadar hasta seçiminin "
            "titizliğidir. Uygun hasta profilinde vNOTES, klasik laparoskopi ve açık "
            "cerrahiye kıyasla belirgin üstünlükler sunar: hiç karın kesisi "
            "olmaması, daha az post-operatif ağrı, daha hızlı günlük yaşama dönüş.</p>"
        ),
        "treatment_approach_en": (
            "<p>Patient suitability for vNOTES requires appropriate anatomy, uterine "
            "size within defined limits, and careful assessment of prior pelvic "
            "surgical history. Every candidate is evaluated with detailed pre-"
            "operative examination and imaging.</p>"
            "<p>What makes the technique safe is not only surgical experience but "
            "meticulous patient selection. In the right candidates, vNOTES offers "
            "clear advantages over both conventional laparoscopy and open surgery: "
            "no abdominal incisions, less post-operative pain, and faster return "
            "to daily life.</p>"
        ),
        "recovery_info_tr": (
            "<p>vNOTES sonrası hastaların büyük çoğunluğu aynı gün içinde mobilize "
            "olur ve 24 saat içinde taburcu edilir. Karın duvarında kesi olmadığı "
            "için klasik ameliyat sonrası karın ağrısı neredeyse yok denecek "
            "kadar azdır.</p>"
            "<p>Cinsel ilişki, ağır kaldırma ve tampon kullanımı gibi aktiviteler "
            "için genellikle 4-6 haftalık bir bekleme süresi önerilir. Kontrol "
            "muayeneleri 10. gün ve 6. hafta olarak planlanır.</p>"
        ),
        "recovery_info_en": (
            "<p>After vNOTES most patients mobilize the same day and are discharged "
            "within 24 hours. Because there are no abdominal incisions, the usual "
            "post-operative abdominal pain is nearly absent.</p>"
            "<p>Sexual intercourse, heavy lifting, and tampon use are generally "
            "restricted for 4-6 weeks. Follow-up visits are scheduled at day 10 "
            "and week 6.</p>"
        ),
        "meta_title_tr": "vNOTES İzsiz Vajinal Cerrahi — Op. Dr. Savaş Gündoğan",
        "meta_title_en": "vNOTES Scarless Vaginal Surgery — M.D. Savaş Gündoğan",
        "meta_description_tr": (
            "Karında iz bırakmayan vajinal minimal invaziv cerrahi (vNOTES). "
            "Histerektomi, kist ve prolapsus için modern yaklaşım."
        ),
        "meta_description_en": (
            "Scarless vaginal minimally invasive surgery (vNOTES) — hysterectomy, "
            "ovarian cysts, and prolapse with a modern approach."
        ),
    },

    # --------------------------------------------------------------
    "uroginekoloji": {
        "full_description_tr": (
            "<p>Ürojinekoloji, idrar kaçırma, pelvik organ sarkması (prolapsus) ve "
            "mesane fonksiyon bozuklukları gibi pelvik taban sorunlarına odaklanan "
            "jinekolojinin alt dalıdır. Bu sorunlar kadının yaşam kalitesini derinden "
            "etkiler — sosyal hayattan egzersize, cinsellikten uykuya kadar her "
            "alanı kapsar.</p>"
            "<p>Konservatif tedavilerden (fizik tedavi, davranışsal değişiklikler, "
            "pesser uygulamaları) minimal invaziv cerrahi yöntemlere kadar geniş "
            "bir yelpazede kişiye özel çözümler sunuyorum.</p>"
        ),
        "full_description_en": (
            "<p>Urogynecology is the subspecialty of gynecology devoted to pelvic "
            "floor disorders — urinary incontinence, pelvic organ prolapse, and "
            "bladder dysfunction. These conditions deeply affect quality of life, "
            "touching everything from social activity and exercise to sexuality "
            "and sleep.</p>"
            "<p>I offer personalized solutions across the full spectrum — from "
            "conservative therapy (pelvic floor physiotherapy, behavioral changes, "
            "pessary fitting) to minimally invasive surgery.</p>"
        ),
        "symptoms_tr": (
            "<p>Pelvik taban bozukluklarının en sık görülen belirtileri:</p>"
            "<ul>"
            "<li>Öksürme, hapşırma ya da ağır kaldırma sırasında idrar kaçırma (stres tipi)</li>"
            "<li>Ani ve dayanılmaz idrar yapma hissi (sıkışma tipi)</li>"
            "<li>Vajinada dolgunluk, sarkma veya kitle hissi</li>"
            "<li>Cinsel ilişkide rahatsızlık ya da memnuniyetsizlik</li>"
            "<li>İdrar yaparken tam boşaltamama hissi, tekrarlayan idrar yolu enfeksiyonları</li>"
            "<li>Makatta bası, dışkılama güçlüğü</li>"
            "</ul>"
        ),
        "symptoms_en": (
            "<p>The most common symptoms of pelvic floor disorders:</p>"
            "<ul>"
            "<li>Leakage with coughing, sneezing, or heavy lifting (stress incontinence)</li>"
            "<li>Sudden, overwhelming urge to urinate (urge incontinence)</li>"
            "<li>Vaginal fullness, bulging, or a sense of something falling out</li>"
            "<li>Discomfort or dissatisfaction during intercourse</li>"
            "<li>Incomplete bladder emptying, recurrent urinary tract infections</li>"
            "<li>Rectal pressure or difficulty with bowel movements</li>"
            "</ul>"
        ),
        "treatment_approach_tr": (
            "<p>Tedavi planı her zaman en az invaziv seçenekten başlar. Birçok hasta "
            "pelvik taban fizik tedavisi, davranışsal değişiklikler ve gerektiğinde "
            "pesser uygulaması ile belirgin rahatlama yaşar. Bu yöntemler yetersiz "
            "kaldığında ya da ileri evre prolapsus söz konusuysa cerrahi seçenekler "
            "devreye girer.</p>"
            "<p>Cerrahide tercih ettiğim yaklaşımlar — TVT/TOT sling operasyonları, "
            "laparoskopik veya robotik sakrokolpopeksi, vajinal prolapsus onarımları — "
            "kadının anatomisine, yaşam tarzına ve beklentisine göre bireysel olarak "
            "planlanır.</p>"
        ),
        "treatment_approach_en": (
            "<p>I always begin with the least invasive option. Many patients "
            "experience meaningful relief with pelvic floor physiotherapy, "
            "behavioral modifications, and, when indicated, a pessary. If these "
            "are insufficient — or if prolapse is advanced — surgical options "
            "enter the conversation.</p>"
            "<p>My preferred surgical approaches — TVT/TOT sling procedures, "
            "laparoscopic or robotic sacrocolpopexy, and vaginal prolapse "
            "repairs — are planned individually based on anatomy, lifestyle, "
            "and expectations.</p>"
        ),
        "recovery_info_tr": (
            "<p>Slinx cerrahisi (idrar kaçırma için) genellikle 24 saat içinde "
            "taburcu olmayı sağlar. Sakrokolpopeksi gibi daha kapsamlı prolapsus "
            "cerrahilerinde 1-2 gün hastanede kalış gerekebilir. İlk 4-6 hafta "
            "ağır kaldırmamak, cinsel ilişkiden uzak durmak ve pelvik taban "
            "egzersizlerini düzenli yapmak başarı için kritiktir.</p>"
            "<p>Uzun dönem takip önemlidir — prolapsus tekrar edebilir, bu nedenle "
            "yıllık kontrol önerilir.</p>"
        ),
        "recovery_info_en": (
            "<p>Sling procedures (for incontinence) typically allow discharge "
            "within 24 hours. More extensive prolapse surgery such as "
            "sacrocolpopexy may require a 1-2 day hospital stay. For the first "
            "4-6 weeks, patients should avoid heavy lifting and intercourse, "
            "and perform pelvic floor exercises consistently — all of which are "
            "critical for lasting success.</p>"
            "<p>Long-term follow-up matters — prolapse can recur, so annual "
            "surveillance is recommended.</p>"
        ),
        "meta_title_tr": "Ürojinekoloji — İdrar Kaçırma ve Prolapsus Tedavisi",
        "meta_title_en": "Urogynecology — Incontinence and Prolapse Treatment",
        "meta_description_tr": (
            "İdrar kaçırma, pelvik organ sarkması ve mesane sorunlarında modern "
            "cerrahi ve konservatif çözümler. Acıbadem Maslak."
        ),
        "meta_description_en": (
            "Modern surgical and conservative treatment for urinary "
            "incontinence, pelvic organ prolapse, and bladder disorders."
        ),
    },

    # --------------------------------------------------------------
    "menopoz-yonetimi": {
        "full_description_tr": (
            "<p>Menopoz bir hastalık değil, bir yaşam evresidir — ancak beraberinde "
            "getirdiği ateş basmaları, uyku bozuklukları, ruh hali dalgalanmaları, "
            "vajinal kuruluk ve kemik yoğunluğu değişiklikleri birçok kadını "
            "etkiler. Doğru yönetildiğinde bu dönem yaşam kalitesinde belirgin "
            "iyileşme sağlanabilir.</p>"
            "<p>Hormon replasman tedavisinden (HRT) bitkisel seçeneklere, lokal "
            "vajinal tedavilerden kemik sağlığı takibine kadar kişiselleştirilmiş "
            "bir yaklaşım sunuyorum.</p>"
        ),
        "full_description_en": (
            "<p>Menopause is not a disease but a life stage — though the hot "
            "flashes, sleep disturbances, mood shifts, vaginal dryness, and bone "
            "density changes it brings can profoundly affect many women. Managed "
            "well, this transition can become a phase of meaningful improvement "
            "in quality of life.</p>"
            "<p>From hormone replacement therapy (HRT) and plant-based options "
            "to local vaginal therapies and bone health monitoring, I offer a "
            "personalized approach.</p>"
        ),
        "symptoms_tr": (
            "<p>Menopoza geçiş döneminde ve sonrasında en sık karşılaşılan belirtiler:</p>"
            "<ul>"
            "<li>Ateş basmaları ve gece terlemeleri</li>"
            "<li>Düzensiz adet dönemleri, ardından adetin kesilmesi</li>"
            "<li>Uyku bozuklukları, yorgunluk</li>"
            "<li>Ruh hali değişiklikleri, anksiyete, konsantrasyon güçlüğü</li>"
            "<li>Vajinal kuruluk, cinsel ilişkide ağrı</li>"
            "<li>İdrar yollarında sık enfeksiyon, idrar kaçırma şikâyetlerinin artması</li>"
            "<li>Eklem ağrıları, kemik yoğunluğunda azalma</li>"
            "<li>Kilo kontrolünde zorluk, metabolik değişiklikler</li>"
            "</ul>"
        ),
        "symptoms_en": (
            "<p>The most common symptoms during and after the menopausal transition:</p>"
            "<ul>"
            "<li>Hot flashes and night sweats</li>"
            "<li>Irregular menstrual cycles, followed by cessation</li>"
            "<li>Sleep disturbances, fatigue</li>"
            "<li>Mood changes, anxiety, concentration difficulties</li>"
            "<li>Vaginal dryness, painful intercourse</li>"
            "<li>Recurrent urinary tract infections, worsening incontinence</li>"
            "<li>Joint aches, decreased bone density</li>"
            "<li>Difficulty with weight control, metabolic changes</li>"
            "</ul>"
        ),
        "treatment_approach_tr": (
            "<p>Her kadının menopoz deneyimi biriciktir — bu nedenle tedavi de "
            "bireyseldir. Hormon replasman tedavisi doğru hasta profilinde son "
            "derece etkili ve güvenlidir, ancak bir risk-fayda değerlendirmesi "
            "olmadan başlanmamalıdır. Ailede meme kanseri öyküsü, kardiyovasküler "
            "risk faktörleri ve pıhtılaşma bozuklukları gibi durumlar mutlaka "
            "değerlendirilir.</p>"
            "<p>HRT dışında vajinal östrojen, lazer uygulamaları, bitkisel destekler "
            "ve yaşam tarzı önerileri — beslenme, fiziksel aktivite, kemik yoğunluğu "
            "takibi — kişiye özel olarak planlanır.</p>"
        ),
        "treatment_approach_en": (
            "<p>Every woman's menopausal experience is unique, so treatment is "
            "individualized. HRT can be extremely effective and safe in the right "
            "patient, but it should never be started without a careful risk-benefit "
            "assessment — family history of breast cancer, cardiovascular risk "
            "factors, and clotting disorders must all be considered.</p>"
            "<p>Beyond systemic HRT, options include local vaginal estrogen, "
            "laser therapy, phytoestrogen supplements, and lifestyle guidance — "
            "nutrition, physical activity, and bone density monitoring — all "
            "tailored to the individual.</p>"
        ),
        "recovery_info_tr": (
            "<p>Menopoz tedavisi bir 'iyileşme süreci' değil, bir 'uyum süreci'dir. "
            "HRT başlandıktan sonra belirtilerde iyileşme genellikle 2-4 hafta "
            "içinde hissedilmeye başlar. Tam etkinin değerlendirilmesi için 3 aylık "
            "kontrol önerilir.</p>"
            "<p>Uzun dönemde yıllık jinekolojik muayene, meme kontrolü ve kemik "
            "yoğunluğu ölçümü tedavi planının ayrılmaz parçalarıdır.</p>"
        ),
        "recovery_info_en": (
            "<p>Menopause care is not a 'recovery process' but an 'adaptation "
            "process'. After HRT is initiated, symptom improvement is usually "
            "noticeable within 2-4 weeks, with full assessment of effectiveness "
            "at a 3-month follow-up.</p>"
            "<p>Over the long term, annual gynecologic examinations, breast "
            "screening, and bone density monitoring are integral parts of the "
            "care plan.</p>"
        ),
        "meta_title_tr": "Menopoz ve Hormon Tedavisi — Op. Dr. Savaş Gündoğan",
        "meta_title_en": "Menopause and Hormone Therapy — M.D. Savaş Gündoğan",
        "meta_description_tr": (
            "Menopoz belirtilerine kişiye özel yaklaşım: hormon tedavisi (HRT), "
            "vajinal tedaviler, kemik sağlığı takibi ve yaşam tarzı danışmanlığı."
        ),
        "meta_description_en": (
            "Personalized menopause care — hormone therapy (HRT), vaginal "
            "treatments, bone health monitoring, and lifestyle guidance."
        ),
    },

    # --------------------------------------------------------------
    "jinekolojik-onkoloji": {
        "full_description_tr": (
            "<p>Jinekolojik onkoloji, kadın üreme sistemini etkileyen kanserlerin — "
            "rahim ağzı (serviks), rahim, yumurtalık, vulva ve vajina — erken tanı, "
            "tedavi ve takibini kapsar. Erken tanı, bu kanserlerde sağkalımı "
            "belirleyen en önemli faktördür.</p>"
            "<p>Tarama ve koruyucu jinekoloji yaklaşımım, klinik muayene, HPV "
            "testi, smear, transvajinal ultrason ve gerektiğinde kolposkopi "
            "gibi yöntemlerin birleşiminden oluşur. Şüpheli bulgularda onkoloji "
            "ekibiyle multidisipliner değerlendirme yaparak hastayı kesintisiz "
            "bir bakım hattında tutuyorum.</p>"
        ),
        "full_description_en": (
            "<p>Gynecologic oncology covers the early detection, treatment, and "
            "follow-up of cancers of the female reproductive tract — cervix, "
            "uterus, ovary, vulva, and vagina. Early detection is the single "
            "most important determinant of survival in these cancers.</p>"
            "<p>My approach to screening and preventive gynecology combines "
            "clinical examination, HPV testing, Pap smear, transvaginal "
            "ultrasound, and — when indicated — colposcopy. For any suspicious "
            "finding, I coordinate multidisciplinary review with the oncology "
            "team, keeping the patient within a seamless care pathway.</p>"
        ),
        "symptoms_tr": (
            "<p>Uyarıcı belirtiler her kanser türüne göre farklılık gösterir, "
            "ancak aşağıdaki bulgular mutlaka değerlendirilmelidir:</p>"
            "<ul>"
            "<li>Adetler arası ya da menopoz sonrası vajinal kanama</li>"
            "<li>Anormal ya da kötü kokulu akıntı</li>"
            "<li>Cinsel ilişki sonrası kanama</li>"
            "<li>Pelvik veya karın alt bölgede ısrarcı ağrı, basınç hissi</li>"
            "<li>Uzun süreli şişkinlik, iştahsızlık, hızlı doyma hissi (yumurtalık kanseri şüphesi)</li>"
            "<li>Vulvada kaşıntı, ülser ya da renk değişikliği</li>"
            "<li>Pozitif HPV testi veya anormal smear sonucu</li>"
            "</ul>"
        ),
        "symptoms_en": (
            "<p>Warning signs differ by cancer type, but the following should "
            "always prompt evaluation:</p>"
            "<ul>"
            "<li>Intermenstrual or post-menopausal vaginal bleeding</li>"
            "<li>Abnormal or foul-smelling discharge</li>"
            "<li>Bleeding after intercourse</li>"
            "<li>Persistent pelvic or lower abdominal pain or pressure</li>"
            "<li>Prolonged bloating, loss of appetite, early satiety (concerning for ovarian cancer)</li>"
            "<li>Vulvar itching, ulceration, or color change</li>"
            "<li>Positive HPV test or abnormal Pap smear</li>"
            "</ul>"
        ),
        "treatment_approach_tr": (
            "<p>Koruyucu jinekoloji hizmetlerim — düzenli smear, HPV aşısı "
            "önerisi, ailede genetik risk varlığında genetik danışmanlık — "
            "tedavinin ilk basamağıdır. Şüpheli bir bulgu saptandığında hızlı, "
            "tam teşekküllü değerlendirme (kolposkopi, biyopsi, görüntüleme) "
            "yapılır.</p>"
            "<p>Erken evre vakalarda minimal invaziv cerrahi (laparoskopik ya da "
            "robotik evreleme) tercih edilir. Kompleks olgularda Acıbadem "
            "jinekolojik onkoloji ekibiyle multidisipliner karar alıyoruz — "
            "hastanın tek bir merkez altında, kesintisiz bir bakım almasını "
            "sağlıyoruz.</p>"
        ),
        "treatment_approach_en": (
            "<p>Preventive gynecology — regular Pap smears, HPV vaccination "
            "counseling, and genetic counseling where family risk exists — is "
            "the first step. If a suspicious finding arises, rapid and "
            "comprehensive evaluation follows (colposcopy, biopsy, imaging).</p>"
            "<p>In early-stage disease, minimally invasive surgery "
            "(laparoscopic or robotic staging) is preferred. For complex cases, "
            "I coordinate multidisciplinary decisions with the Acıbadem "
            "gynecologic oncology team — ensuring the patient receives "
            "seamless care within a single center.</p>"
        ),
        "recovery_info_tr": (
            "<p>Minimal invaziv onkolojik cerrahi sonrası taburculuk genellikle "
            "1-3 gün içinde gerçekleşir. Postoperatif takip, patoloji sonuçları "
            "ve gerekiyorsa ek tedavi (kemoterapi, radyoterapi) planlaması "
            "multidisipliner olarak yapılır.</p>"
            "<p>Kanser sonrası takip protokolleri hastalığın evresine ve tedavi "
            "yanıtına göre bireysel olarak belirlenir — genellikle ilk 2 yıl "
            "3-4 aylık, sonraki 3 yıl 6 aylık, sonra yıllık kontrollerle devam "
            "edilir.</p>"
        ),
        "recovery_info_en": (
            "<p>After minimally invasive oncologic surgery, discharge typically "
            "occurs within 1-3 days. Post-operative follow-up, pathology "
            "results, and — if needed — adjuvant treatment (chemotherapy, "
            "radiation) are planned through multidisciplinary review.</p>"
            "<p>Post-cancer surveillance protocols are individualized to stage "
            "and treatment response — usually every 3-4 months for the first 2 "
            "years, every 6 months for the next 3 years, and annually "
            "thereafter.</p>"
        ),
        "meta_title_tr": "Jinekolojik Onkoloji ve Tarama — Op. Dr. Savaş Gündoğan",
        "meta_title_en": "Gynecologic Oncology and Screening — M.D. Savaş Gündoğan",
        "meta_description_tr": (
            "Serviks, rahim ve yumurtalık kanserlerinde tarama, erken tanı ve "
            "minimal invaziv cerrahi. Acıbadem multidisipliner onkoloji yaklaşımı."
        ),
        "meta_description_en": (
            "Screening, early detection, and minimally invasive surgery for "
            "cervical, uterine, and ovarian cancers within Acıbadem's "
            "multidisciplinary oncology framework."
        ),
    },

    # --------------------------------------------------------------
    "gebelik-takibi": {
        "full_description_tr": (
            "<p>Gebelik, yaşamın en anlamlı yolculuklarından biridir — ve doğru "
            "takip edildiğinde bu dönem hem anne hem bebek için güvenli ve "
            "keyifli bir süreç olabilir. Preimplantasyon döneminden doğuma, "
            "hatta lohusalık dönemine kadar kesintisiz bir bakım sunuyorum.</p>"
            "<p>Riskli gebelikler, çoğul gebelikler ve özel hasta profilleri "
            "(ileri anne yaşı, kronik hastalıklar, önceki obstetrik "
            "komplikasyon öyküsü) için ek dikkat ve multidisipliner yaklaşım "
            "gerektiren yönetim planları hazırlıyorum.</p>"
        ),
        "full_description_en": (
            "<p>Pregnancy is one of life's most meaningful journeys — and with "
            "proper follow-up, it can be a safe and fulfilling experience for "
            "both mother and baby. I provide continuous care from "
            "preimplantation through delivery, extending into the postpartum "
            "period.</p>"
            "<p>For high-risk pregnancies, multiple gestations, and special "
            "patient profiles (advanced maternal age, chronic illness, prior "
            "obstetric complications), I develop management plans that require "
            "additional attention and a multidisciplinary approach.</p>"
        ),
        "symptoms_tr": (
            "<p>Her trimester kendine özgü değerlendirme ve takipler gerektirir. "
            "Standart gebelik takibim aşağıdaki basamakları kapsar:</p>"
            "<ul>"
            "<li>İlk trimester (6-13. hafta): gebelik tespiti, NT (ense saydamlığı) taraması, "
            "kan grubu ve temel laboratuvar</li>"
            "<li>İkinci trimester (14-27. hafta): detaylı anomali ultrasonu (18-22. hafta), "
            "gestasyonel diyabet taraması (24-28. hafta)</li>"
            "<li>Üçüncü trimester (28-40. hafta): fetal büyüme takibi, doppler ölçümleri, "
            "NST, doğum planlaması</li>"
            "<li>Ek olarak: preeklampsi riski taraması, tiroid fonksiyonları, "
            "D vitamini ve demir takibi</li>"
            "</ul>"
        ),
        "symptoms_en": (
            "<p>Each trimester brings its own assessments. My standard "
            "pregnancy follow-up covers:</p>"
            "<ul>"
            "<li>First trimester (weeks 6-13): pregnancy confirmation, nuchal translucency "
            "screening, blood type and baseline labs</li>"
            "<li>Second trimester (weeks 14-27): detailed anatomy ultrasound (weeks 18-22), "
            "gestational diabetes screening (weeks 24-28)</li>"
            "<li>Third trimester (weeks 28-40): fetal growth monitoring, Doppler studies, "
            "non-stress tests, delivery planning</li>"
            "<li>Plus: preeclampsia risk screening, thyroid function, vitamin D and iron</li>"
            "</ul>"
        ),
        "treatment_approach_tr": (
            "<p>Her gebeliği tek bir şablonla değil, annenin tıbbi öyküsüne, "
            "gebeliğin seyrine ve kişisel tercihlerine göre şekillendiriyorum. "
            "Normal doğum ve sezaryen arasında karar verirken tıbbi endikasyonları, "
            "annenin ve bebeğin güvenliğini ve ailenin tercihlerini birlikte "
            "değerlendiriyorum.</p>"
            "<p>Doğum sonrası izlem de en az gebelik kadar önemlidir. Emzirme "
            "desteği, postpartum depresyon taraması, pelvik taban iyileşmesi ve "
            "jinekolojik kontroller — hepsi bakım planımın parçasıdır.</p>"
        ),
        "treatment_approach_en": (
            "<p>I do not apply a single template to every pregnancy — care is "
            "shaped by the mother's medical history, the course of the "
            "pregnancy, and her personal preferences. When deciding between "
            "vaginal birth and cesarean, medical indications, maternal-fetal "
            "safety, and family preferences are weighed together.</p>"
            "<p>Post-partum follow-up matters as much as the pregnancy itself. "
            "Breastfeeding support, postpartum depression screening, pelvic "
            "floor recovery, and routine gynecologic follow-up are all part "
            "of the care plan.</p>"
        ),
        "recovery_info_tr": (
            "<p>Normal doğum sonrası genellikle 1-2 gün, sezaryen sonrası 2-3 gün "
            "hastanede kalış olur. İlk 6 haftalık lohusalık sürecinde haftalık "
            "ya da iki haftalık kontroller planlıyoruz. Bu dönemde emzirme, "
            "yara iyileşmesi, ruhsal sağlık ve uyku dengesi önceliklidir.</p>"
            "<p>Altı hafta sonundaki kontrolde tam jinekolojik muayene yapılır, "
            "pelvik taban değerlendirilir ve yeniden gebelik planlaması için "
            "aile planlaması konuşulur.</p>"
        ),
        "recovery_info_en": (
            "<p>Hospital stay is typically 1-2 days after vaginal delivery and "
            "2-3 days after cesarean. Weekly or biweekly follow-ups are "
            "scheduled across the 6-week postpartum period, prioritizing "
            "breastfeeding, wound healing, mental health, and sleep.</p>"
            "<p>At the 6-week visit, a full gynecologic exam is performed, "
            "the pelvic floor is assessed, and family planning is discussed "
            "for future pregnancy timing.</p>"
        ),
        "meta_title_tr": "Gebelik Takibi ve Doğum — Op. Dr. Savaş Gündoğan",
        "meta_title_en": "Pregnancy Follow-up and Delivery — M.D. Savaş Gündoğan",
        "meta_description_tr": (
            "Sağlıklı gebelik için kesintisiz obstetrik takip: trimester "
            "muayeneleri, anomali taramaları, riskli gebelik yönetimi ve doğum."
        ),
        "meta_description_en": (
            "Seamless obstetric care — trimester exams, anomaly screening, "
            "high-risk pregnancy management, and delivery."
        ),
    },
}


# =====================================================================
# EDUCATION DESCRIPTIONS
# =====================================================================
EDUCATION_DESCRIPTIONS = {
    "İnönü": {
        "tr": (
            "Altı yıllık Türk tıp eğitimini Malatya İnönü Üniversitesi Tıp Fakültesi'nde "
            "tamamladım. Temel bilimler, klinik rotasyonlar ve hasta odaklı pratik "
            "eğitim bu dönemde hekimlik anlayışımın temelini oluşturdu."
        ),
        "en": (
            "I completed my six-year medical education at İnönü University Faculty of "
            "Medicine in Malatya. The combination of basic sciences, clinical "
            "rotations, and patient-centered training laid the foundation of my "
            "approach to medicine."
        ),
    },
    "Acıbadem Mehmet Ali": {
        "tr": (
            "Kadın Hastalıkları ve Doğum uzmanlık eğitimimi Acıbadem Mehmet Ali "
            "Aydınlar Üniversitesi Tıp Fakültesi'nde tamamladım. Bu dönemde yüksek "
            "hasta çeşitliliği, akademik araştırma fırsatları ve deneyimli hocalarımın "
            "mentorluğunda minimal invaziv cerrahi ilgimi derinleştirdim."
        ),
        "en": (
            "I completed my residency in Obstetrics and Gynecology at Acıbadem Mehmet "
            "Ali Aydınlar University School of Medicine. High patient diversity, "
            "academic research opportunities, and mentorship from experienced "
            "faculty allowed me to deepen my interest in minimally invasive surgery."
        ),
    },
    "Università degli Studi dell'Insubria": {
        "tr": (
            "İtalya'daki Università degli Studi dell'Insubria bünyesinde minimal "
            "invaziv jinekolojik cerrahi eğitimi aldım. Avrupa'nın önde gelen "
            "merkezlerinden birinde laparoskopi, robotik cerrahi ve vNOTES "
            "tekniklerini deneyimleyerek uluslararası standartları pratiğime taşıdım."
        ),
        "en": (
            "I pursued advanced training in minimally invasive gynecologic surgery at "
            "Università degli Studi dell'Insubria in Italy. At one of Europe's "
            "leading centers I gained experience with laparoscopy, robotic surgery, "
            "and vNOTES — carrying international standards into my practice."
        ),
    },
}


# =====================================================================
# EXPERIENCE DESCRIPTIONS (keyed by a distinctive fragment)
# =====================================================================
EXPERIENCE_DESCRIPTIONS = {
    "intörn": {  # İntörn Hekim
        "tr": (
            "Tıp fakültesinin son yılında tüm kliniklerde rotasyon yaparak hasta "
            "yönetiminde ekip içinde çalışma kültürünü kazandım."
        ),
        "en": (
            "During the final year of medical school I rotated through all clinical "
            "departments, learning team-based patient care firsthand."
        ),
    },
    "üroloji": {  # Üroloji Asistanı
        "tr": (
            "Kısa süreli üroloji rotasyonum, pelvik anatomi ve ürojinekolojik "
            "problemlere olan ilgimin ilk temelini oluşturdu. Bu deneyim, sonraki "
            "dönemde ürojinekoloji alanına özel ilgi duymamı sağladı."
        ),
        "en": (
            "A brief urology rotation built my initial interest in pelvic anatomy "
            "and urogynecologic problems — a foundation that later shaped my "
            "focus on urogynecology."
        ),
    },
    "pratisyen": {  # Pratisyen Hekim
        "tr": (
            "Birinci basamak sağlık hizmetinde görev yaparken geniş bir hasta "
            "yelpazesine danışmanlık yaptım. Bu dönem, koruyucu hekimlik ve "
            "hasta-hekim iletişiminin değerini derinden öğrendiğim bir aşama oldu."
        ),
        "en": (
            "Working in primary care, I served a wide range of patients and "
            "deepened my appreciation of preventive medicine and the "
            "patient-physician relationship."
        ),
    },
    "araştırma görevlisi": {  # Araştırma Görevlisi Hekim
        "tr": (
            "Acıbadem Üniversitesi'nde araştırma görevlisi olarak hem klinik "
            "pratiği sürdürdüm hem de uluslararası dergilerde yayınlanan "
            "bilimsel çalışmalara katkıda bulundum. Akademik titizlik ve "
            "kanıta dayalı tıp prensipleri bu dönemde pekişti."
        ),
        "en": (
            "As a research fellow at Acıbadem University I continued clinical "
            "work while contributing to internationally published research. "
            "Academic rigor and evidence-based medicine became core principles "
            "during this period."
        ),
    },
    "başasistan": {  # Başasistan — Kadın Hastalıkları ve Doğum
        "tr": (
            "Başasistanlık görevim sırasında genç asistan hekimlerin eğitiminde "
            "rol aldım, kompleks vakaların yönetiminde daha fazla sorumluluk "
            "üstlendim ve klinik karar alma becerimi olgunlaştırdım."
        ),
        "en": (
            "In my role as chief resident I helped train junior residents, took "
            "on greater responsibility in managing complex cases, and matured "
            "my clinical decision-making."
        ),
    },
    "Kadın Hastalıkları ve Doğum Uzmanı": {  # multiple uzman positions
        "tr": (
            "Kadın Hastalıkları ve Doğum Uzmanı olarak aktif klinik pratik "
            "yürütüyor, minimal invaziv cerrahi vakalarımı ağırlıklı olarak "
            "bu pozisyon çerçevesinde gerçekleştiriyorum. Hasta değerlendirmesi, "
            "cerrahi planlama, ameliyathane pratiği ve uzun dönem takip bu "
            "rolün merkezinde yer alıyor."
        ),
        "en": (
            "As an attending specialist in Obstetrics and Gynecology, I maintain "
            "active clinical practice and perform the majority of my minimally "
            "invasive surgical cases within this role. Patient evaluation, "
            "surgical planning, operative practice, and long-term follow-up are "
            "at its core."
        ),
    },
}


# =====================================================================
# KVKK (Turkish personal data protection notice) & PRIVACY POLICY
# =====================================================================
KVKK_TR = (
    "<h3>Aydınlatma Metni</h3>"
    "<p>Op. Dr. Savaş Gündoğan tarafından, 6698 sayılı Kişisel Verilerin Korunması "
    "Kanunu (\"KVKK\") uyarınca, veri sorumlusu sıfatıyla aşağıdaki bilgilendirmenin "
    "dikkatinize sunulduğunu belirtiriz.</p>"
    "<h4>1. Toplanan Kişisel Veriler</h4>"
    "<p>İletişim formu aracılığıyla: ad-soyad, e-posta adresi, telefon numarası "
    "(isteğe bağlı), mesaj içeriği. Site ziyaretlerinde: anonim sayfa görüntüleme "
    "verileri, cihaz bilgileri ve genel konum (ülke düzeyinde). Sağlık verileriniz "
    "iletişim formu üzerinden paylaşılmamalıdır; bu tür bilgiler yalnızca resmi "
    "randevu ve muayene kanalları aracılığıyla alınır.</p>"
    "<h4>2. Verilerin İşlenme Amaçları</h4>"
    "<p>Randevu ve bilgi taleplerinizi yanıtlamak, yasal yükümlülükleri yerine "
    "getirmek ve site deneyimini iyileştirmek.</p>"
    "<h4>3. Verilerin Aktarımı</h4>"
    "<p>Kişisel verileriniz, açık rızanız olmaksızın üçüncü kişilerle "
    "paylaşılmamaktadır. Yalnızca teknik altyapı sağlayıcılarımız (hosting, "
    "e-posta servisi) yasal olarak zorunlu olduğu ölçüde verilere erişebilir.</p>"
    "<h4>4. Haklarınız</h4>"
    "<p>KVKK'nın 11. maddesi uyarınca verilerinize erişme, düzeltilmesini, "
    "silinmesini talep etme ve itiraz hakkına sahipsiniz. Taleplerinizi "
    "<a href=\"mailto:savas.gundogan@acibadem.com\">savas.gundogan@acibadem.com</a> "
    "adresine iletebilirsiniz.</p>"
    "<p><em>Son güncelleme: Nisan 2026</em></p>"
)

KVKK_EN = (
    "<h3>Privacy and Data Protection Notice</h3>"
    "<p>This notice is provided by Op. Dr. Savaş Gündoğan as the data controller "
    "under the Turkish Personal Data Protection Law No. 6698 (\"KVKK\") and, where "
    "applicable, the EU General Data Protection Regulation (GDPR).</p>"
    "<h4>1. Personal Data Collected</h4>"
    "<p>Via the contact form: name, email address, phone number (optional), and "
    "message content. During site visits: anonymous page-view data, device "
    "information, and general location (country level). Please do not share "
    "health data through the contact form — such information should be shared "
    "only through official appointment and consultation channels.</p>"
    "<h4>2. Purposes of Processing</h4>"
    "<p>To respond to your appointment and information requests, comply with "
    "legal obligations, and improve the website experience.</p>"
    "<h4>3. Data Sharing</h4>"
    "<p>Your personal data is not shared with third parties without your explicit "
    "consent. Only technical infrastructure providers (hosting, email) may have "
    "access, strictly as legally required.</p>"
    "<h4>4. Your Rights</h4>"
    "<p>Under KVKK Article 11 (and equivalent GDPR provisions), you have the "
    "right to access, correct, delete, or object to the processing of your "
    "personal data. Requests may be directed to "
    "<a href=\"mailto:savas.gundogan@acibadem.com\">"
    "savas.gundogan@acibadem.com</a>.</p>"
    "<p><em>Last updated: April 2026</em></p>"
)

PRIVACY_TR = (
    "<h3>Gizlilik Politikası</h3>"
    "<p>Bu gizlilik politikası, Op. Dr. Savaş Gündoğan resmi web sitesinde "
    "(drsavasgundogan.com) geçerli olup ziyaretçilerin mahremiyetini korumayı "
    "amaçlar.</p>"
    "<h4>Çerez Kullanımı</h4>"
    "<p>Sitemizde yalnızca site işlevselliği ve anonim ziyaretçi istatistikleri "
    "için gerekli olan çerezler kullanılmaktadır. Reklam izleme veya üçüncü "
    "taraf profilleme çerezi kullanılmamaktadır.</p>"
    "<h4>Bilgi Güvenliği</h4>"
    "<p>Site trafiği SSL/TLS ile şifrelenir. Kişisel veriler şifreli sunucularda "
    "tutulur ve yetkili olmayan erişime karşı korunur.</p>"
    "<h4>Harici Bağlantılar</h4>"
    "<p>Sitemiz zaman zaman üçüncü taraf kaynaklara (akademik makaleler, "
    "Acıbadem web sayfası, sosyal medya hesapları) bağlantı verir. Bu sitelerin "
    "gizlilik politikaları bağımsızdır ve sorumluluğumuz dışındadır.</p>"
    "<h4>Değişiklikler</h4>"
    "<p>Bu politika güncellenebilir. Son güncelleme tarihi metnin sonunda yer alır.</p>"
    "<p><em>Son güncelleme: Nisan 2026</em></p>"
)

PRIVACY_EN = (
    "<h3>Privacy Policy</h3>"
    "<p>This privacy policy applies to the official website of Op. Dr. Savaş "
    "Gündoğan (drsavasgundogan.com) and is intended to protect visitors' privacy.</p>"
    "<h4>Cookie Usage</h4>"
    "<p>We use only cookies necessary for site functionality and anonymous "
    "visitor analytics. We do not use advertising trackers or third-party "
    "profiling cookies.</p>"
    "<h4>Information Security</h4>"
    "<p>Site traffic is encrypted via SSL/TLS. Personal data is stored on "
    "encrypted servers and protected against unauthorized access.</p>"
    "<h4>External Links</h4>"
    "<p>Our site occasionally links to third-party resources (academic "
    "articles, the Acıbadem website, social media accounts). The privacy "
    "policies of those sites are independent and fall outside our "
    "responsibility.</p>"
    "<h4>Changes</h4>"
    "<p>This policy may be updated. The last revision date is shown at the "
    "end of the document.</p>"
    "<p><em>Last updated: April 2026</em></p>"
)


# =====================================================================
# COMMAND
# =====================================================================
class Command(BaseCommand):
    help = "Fill empty content fields with professional TR+EN copy (idempotent)."

    @transaction.atomic
    def handle(self, *args, **opts):
        self._fill_site_settings()
        self._fill_specialties()
        self._fill_education()
        self._fill_experience()
        self.stdout.write(self.style.SUCCESS("Done. Re-run safely — only empty fields are touched."))

    # ----------------------------------------------------------
    def _fill_site_settings(self):
        s = SiteSettings.load()
        changed = False
        if _set_if_empty(s, "kvkk_body_tr", KVKK_TR): changed = True
        if _set_if_empty(s, "kvkk_body_en", KVKK_EN): changed = True
        if _set_if_empty(s, "privacy_body_tr", PRIVACY_TR): changed = True
        if _set_if_empty(s, "privacy_body_en", PRIVACY_EN): changed = True
        if changed:
            s.save()
            self.stdout.write(self.style.SUCCESS("  [ok] SiteSettings KVKK/Privacy filled"))
        else:
            self.stdout.write("  [=] SiteSettings already has KVKK/Privacy")

    # ----------------------------------------------------------
    def _fill_specialties(self):
        for slug, fields in SPECIALTY_CONTENT.items():
            try:
                area = SpecialtyArea.objects.get(slug=slug)
            except SpecialtyArea.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  [skip] SpecialtyArea slug='{slug}' not found"))
                continue
            changed_fields = []
            for fname, val in fields.items():
                if _set_if_empty(area, fname, val):
                    changed_fields.append(fname)
            if changed_fields:
                area.save()
                self.stdout.write(self.style.SUCCESS(
                    f"  [ok] SpecialtyArea '{slug}' filled {len(changed_fields)} fields"
                ))
            else:
                self.stdout.write(f"  [=] SpecialtyArea '{slug}' already complete")

    # ----------------------------------------------------------
    def _fill_education(self):
        for edu in Education.objects.all():
            inst = edu.institution_tr or ""
            content = None
            for key, c in EDUCATION_DESCRIPTIONS.items():
                if key.lower() in inst.lower():
                    content = c
                    break
            if content is None:
                continue
            changed = False
            if _set_if_empty(edu, "description_tr", content["tr"]): changed = True
            if _set_if_empty(edu, "description_en", content["en"]): changed = True
            if changed:
                edu.save()
                self.stdout.write(self.style.SUCCESS(f"  [ok] Education '{inst[:50]}' filled"))

    # ----------------------------------------------------------
    def _fill_experience(self):
        for exp in Experience.objects.all():
            position = (exp.position_tr or "").lower()
            content = None
            # Match longer keys first to avoid generic "uzman" eating all
            matched_key = None
            for key in sorted(EXPERIENCE_DESCRIPTIONS.keys(), key=len, reverse=True):
                if key.lower() in position:
                    matched_key = key
                    content = EXPERIENCE_DESCRIPTIONS[key]
                    break
            if content is None:
                continue
            changed = False
            if _set_if_empty(exp, "description_tr", content["tr"]): changed = True
            if _set_if_empty(exp, "description_en", content["en"]): changed = True
            if changed:
                exp.save()
                self.stdout.write(self.style.SUCCESS(
                    f"  [ok] Experience '{exp.position_tr[:50]}' @ {exp.institution_tr[:40]} filled ({matched_key})"
                ))
