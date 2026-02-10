import streamlit as st
import json
from collections import defaultdict
from io import BytesIO

# Bu modüllerin projenizde var olduğu varsayılmaktadır
from assign_courses import assign_courses_to_curriculum
from gpa_calculator import calculate_gpa, GRADE_POINTS
from parse_transcript import parse_transcript_pdf


# ======================================================
# TRANSLATION DICTIONARY
# ======================================================
TRANSLATIONS = {
    "EN": {
        "page_title": "GPA Planner",
        "upload_header": "📄 Upload Transcript",
        "upload_button": "Upload transcript (PDF)",
        "info_message": "ℹ️ This application currently works only for **MEF University Industrial Engineering** undergraduate programme. Curriculum support for other departments or universities has not been added yet.",
        "upload_prompt": "👈 Please upload your transcript PDF to begin",
        "how_it_works": "❓ How does it work?",
        "step1_title": "**1. Upload your transcript**",
        "step1_desc": "Upload your official transcript as a PDF.\nYour courses, grades, and credits will be read automatically.",
        "step2_title": "**2. Match your courses**",
        "step2_desc": "Assign your completed courses to curriculum slots.\nConfirm once everything looks right.",
        "step3_title": "**3. Explore your GPA**",
        "step3_desc": "Change grades, test scenarios, and instantly see GPA updates.",
        "step_footer": "✨ Plan ahead with confidence.",
        "parse_success": "Transcript parsed successfully ✅",
        "curriculum_title": "📘 Curriculum Overview",
        "semester": "Semester",
        "select_elective": "Select elective",
        "grade": "Grade",
        "total_credits_semester": "Total credits this semester",
        "extra": "+extra",
        "additional_courses": "📚 Additional Courses",
        "additional_courses_caption": "Do you have courses that should be included in your GPA but couldn't match them? Add them here.",
        "add_course": "➕ ADD COURSE",
        "additional_course": "Additional course",
        "confirm_matching": "✅ Confirm matching",
        "matching_confirmed_success": "Matching confirmed. GPA exploration unlocked 🔓",
        "matching_locked": "🔒 Matching confirmed. You can freely edit grades.",
        "current_summary": "📊 Current Summary",
        "gpa": "🎓 GPA",
        "total_credits": "📚 Total Credits",
        "unlock_matching": "Unlock",
        "add_manual_course": "➕ ADD MANUAL COURSE",
        "course_code": "Course Code",
        "credits": "Credits",
        "course_code_required": "⚠️ Please enter a course code",
        "add_course_hint": "📋 For courses from your transcript",
        "add_manual_course_hint": "✍️ For transfer credits or minor/double major courses",
        "additional_courses_info_title": "ℹ️ Which button should I use?",
        "additional_courses_info_text": """
**Add Course (from transcript):** Use this if your course appears on your transcript but wasn't automatically matched to the curriculum.

**Add Manual Course:** Use this for:
- Transfer credits from other universities
- Minor or double major courses
- Courses taken but not yet on your transcript
        """,
        "how_to_download_transcript": "📥 How to download your transcript?",
        "download_instructions": """
**For MEF University students:**

1. 🌐 Go to your **Student Information System (SIS)** portal
2. 📄 From the sidebar menu, select the **2nd option from the top** (document icon)
3. ✅ Click on **"Transcript - QR Coded"** option
4. 💾 Download the PDF file
5. ⬆️ Upload it here using the button on the left sidebar

**For students from other universities:** Check your university's student portal for transcript download options. Look for terms like "Academic Transcript", "Grade Report", or "Transcript PDF".
        """,
    },
    "TR": {
        "page_title": "Not Ortalaması Planlayıcı",
        "upload_header": "📄 Transkript Yükle",
        "upload_button": "Transkript yükle (PDF)",
        "info_message": "ℹ️ Bu uygulama şu anda yalnızca **MEF Üniversitesi Endüstri Mühendisliği** lisans programı için çalışmaktadır. Diğer bölümler veya üniversiteler için müfredat desteği henüz eklenmemiştir.",
        "upload_prompt": "👈 Başlamak için lütfen transkript PDF'inizi yükleyin",
        "how_it_works": "❓ Nasıl çalışır?",
        "step1_title": "**1. Transkriptinizi yükleyin**",
        "step1_desc": "Resmi transkriptinizi PDF olarak yükleyin.\nDersleriniz, notlarınız ve kredileriniz otomatik olarak okunacak.",
        "step2_title": "**2. Derslerinizi eşleştirin**",
        "step2_desc": "Tamamladığınız dersleri müfredat slotlarına atayın.\nHer şey doğru göründüğünde onaylayın.",
        "step3_title": "**3. Not ortalamanızı keşfedin**",
        "step3_desc": "Notları değiştirin, senaryoları test edin ve GPA güncellemelerini anında görün.",
        "step_footer": "✨ Güvenle ileriye planlayın.",
        "parse_success": "Transkript başarıyla ayrıştırıldı ✅",
        "curriculum_title": "📘 Müfredat Görünümü",
        "semester": "Dönem",
        "select_elective": "Seçmeli ders seçin",
        "grade": "Not",
        "total_credits_semester": "Bu dönem toplam kredi",
        "extra": "+ekstra",
        "additional_courses": "📚 Ek Dersler",
        "additional_courses_caption": "Not ortalamanıza dahil edilmesi gereken ancak eşleştiremediğiniz dersler var mı? Buraya ekleyin.",
        "add_course": "➕ DERS EKLE",
        "additional_course": "Ek ders",
        "confirm_matching": "✅ Eşleştirmeyi onayla",
        "matching_confirmed_success": "Eşleştirme onaylandı. GPA keşfi kilidi açıldı 🔓",
        "matching_locked": "🔒 Eşleştirme onaylandı. Notları serbestçe düzenleyebilirsiniz.",
        "current_summary": "📊 Güncel Özet",
        "gpa": "🎓 GPA",
        "total_credits": "📚 Toplam Kredi",
        "unlock_matching": "Kilidi Aç",
        "add_manual_course": "➕ MANUEL DERS EKLE",
        "course_code": "Ders Kodu",
        "credits": "Kredi",
        "course_code_required": "⚠️ Lütfen bir ders kodu girin",
        "add_course_hint": "📋 Transkriptinizdeki dersler için",
        "add_manual_course_hint": "✍️ Transfer veya yandal/çift anadal dersleri için",
        "additional_courses_info_title": "ℹ️ Hangi butonu kullanmalıyım?",
        "additional_courses_info_text": """
**Ders Ekle (transkriptten):** Dersiniz transkriptinizde görünüyor ancak müfredata otomatik eşleşmedi ise bunu kullanın.

**Manuel Ders Ekle:** Şunlar için kullanın:
- Diğer üniversitelerden transfer edilen dersler
- Yandal veya çift anadal dersleri
- Alınan ancak henüz transkripte işlenmemiş dersler
        """,
        "how_to_download_transcript": "📥 Transkriptinizi nasıl indirebilirsiniz?",
        "download_instructions": """
**MEF Üniversitesi öğrencileri için:**

1. 🌐 **Öğrenci Bilgi Sistemi (ÖBS)** portalınıza giriş yapın
2. 📄 Yan menüden **üstten 2. seçeneği** seçin (belge simgesi)
3. ✅ **"Transkript - QR Kodlu"** seçeneğine tıklayın
4. 💾 PDF dosyasını indirin
5. ⬆️ Sol menüdeki butonu kullanarak buraya yükleyin

**Diğer üniversite öğrencileri için:** Üniversitenizin öğrenci portalında transkript indirme seçeneklerini kontrol edin. "Akademik Transkript", "Not Dökümü" veya "Transkript PDF" gibi terimleri arayın.
        """,
    }
}

def t(key):
    """Translation helper function"""
    return TRANSLATIONS[st.session_state.lang].get(key, key)


# ======================================================
# CONFIG
# ======================================================
st.set_page_config(page_title="GPA Planner", layout="wide")

SEMESTER_TARGET_CREDIT = 30

GRADE_OPTIONS = [
    "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+","D", "F","S"
]

PLANNED_GRADE_OPTIONS = ["—"] + GRADE_OPTIONS  


# ======================================================
# CANONICAL COURSE MAPPING
# ======================================================
DERS_CODE_MAPPING = {
    "HISTR 211": "HISTR 213",
    "HISTR 212": "HISTR 214",
    "TURK 111": "TURK 113",
    "TURK 112": "TURK 114",
}
def keep_last_attempt(courses):
    last_seen = {}
    for c in courses:
        code = c["code"]
        last_seen[code] = c
    return list(last_seen.values())

def apply_canonical_mapping(courses, mapping):
    normalized = []

    for c in courses:
        canonical = mapping.get(c["code"], c["code"])
        c = c.copy()
        c["original_code"] = c["code"]
        c["code"] = canonical
        normalized.append(c)

    return normalized

def reset_app_state():
    """Tüm uygulama verilerini temizler"""
    keys_to_clear = [
        "assignments", 
        "unassigned_courses", 
        "mufredat_disi_slots", 
        "matching_confirmed", 
        "locked_gpa"
    ]
    for key in keys_to_clear:
        st.session_state.pop(key, None)
        
    # Planlanan ders verilerini temizle
    keys_to_remove = [key for key in st.session_state.keys() if key.startswith("planned_")]
    for key in keys_to_remove:
        st.session_state.pop(key, None)

# ======================================================
# SIDEBAR — LANGUAGE SELECTOR
# ======================================================
if "lang" not in st.session_state:
    st.session_state.lang = "EN"

# Dil Seçici
current_selection = st.sidebar.selectbox(
    "Language selector",
    ["TR", "EN"],
    format_func=lambda x: "🇹🇷 Türkçe" if x == "TR" else "🇬🇧 English",
    label_visibility="collapsed",
    index=0 if st.session_state.lang == "TR" else 1,
    key="lang_selector_widget"
)

# Dil değiştiğinde - SADECE dil değişikliğini kaydet, rerun yapma
if current_selection != st.session_state.lang:
    st.session_state.lang = current_selection
    # st.rerun() satırını KALDIR - Streamlit otomatik olarak rerun yapacak

st.sidebar.markdown("---")


# ======================================================
# SIDEBAR — UPLOAD LOGIC & DYNAMIC VIEW
# ======================================================
st.sidebar.header(t("upload_header"))

if st.session_state.get("pdf_bytes") is None:
    uploaded_pdf = st.sidebar.file_uploader(
        t("upload_button"),
        type=["pdf"],
        key="pdf_uploader",
        label_visibility="collapsed" # Etiketi gizleyerek alanı daraltır
    )

    if uploaded_pdf is not None:
        st.session_state.file_key_chk = f"{uploaded_pdf.name}_{uploaded_pdf.size}"
        st.session_state.pdf_bytes = uploaded_pdf.getvalue()
        st.session_state.pdf_filename = uploaded_pdf.name
        reset_app_state()
        st.rerun()
else:
    # Dosya yüklendiğinde görünecek kısım
    filename = st.session_state.get("pdf_filename", "transcript.pdf")
    st.sidebar.info(f"📄 {filename}")
    
    back_label = "⬅️ Yeni Transkript Yükle" if st.session_state.lang == "TR" else "⬅️ Upload New Transcript"
    if st.sidebar.button(back_label, use_container_width=True):
        st.session_state.file_key_chk = None
        st.session_state.pdf_bytes = None
        st.session_state.pop("pdf_filename", None)
        reset_app_state()
        st.rerun()

st.sidebar.markdown("<br>", unsafe_allow_html=True) # Hafif bir boşluk

# ======================================================
# LOAD CURRICULUM & MAIN FLOW
# ======================================================
with open("curriculum.json", encoding="utf-8") as f:
    curriculum = json.load(f)

st.info(t("info_message"))

# Ana kontrol: Session state'de PDF verisi var mı?
# Not: uploaded_pdf widget'ı dil değişiminde dosya tutmaya devam etse de
# biz asıl veriyi st.session_state.pdf_bytes içinde saklıyoruz.
if st.session_state.get("pdf_bytes") is None:
    # Dosya yoksa başlangıç ekranını göster
    st.info(t("upload_prompt"))
    
    st.markdown("""
        <style>
        div[data-testid="stExpander"] {
            background-color: #d4e6f1;
            border-radius: 0.5rem;
            padding: 0.5rem;
        }
        div[data-testid="stExpander"] details summary {
            background-color: #d4e6f1;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.expander(t("how_to_download_transcript"), expanded=False):
        st.markdown(t("download_instructions"))
    
    st.markdown(f"### {t('how_it_works')}")
    st.markdown(f"""
{t('step1_title')}  
{t('step1_desc')}

{t('step2_title')}  
{t('step2_desc')}

{t('step3_title')}  
{t('step3_desc')}

{t('step_footer')}
""")
    st.stop()  # Uygulamayı burada durdur

# ======================================================
# PARSE TRANSCRIPT (Veri varsa burası çalışır)
# ======================================================
final_pdf_file = BytesIO(st.session_state.pdf_bytes)

# Parse işlemi
raw_courses = parse_transcript_pdf(final_pdf_file)

mapped_courses = apply_canonical_mapping(
    raw_courses, DERS_CODE_MAPPING
)

student_courses = keep_last_attempt(mapped_courses)
# ======================================================
# INIT SESSION (Verileri başlat veya koru)
# ======================================================
if "assignments" not in st.session_state:
    assignments, unassigned = assign_courses_to_curriculum(
        student_courses, curriculum
    )
    st.session_state.assignments = assignments
    st.session_state.unassigned_courses = unassigned

if "mufredat_disi_slots" not in st.session_state:
    st.session_state.mufredat_disi_slots = []

if "matching_confirmed" not in st.session_state:
    st.session_state.matching_confirmed = False

if "locked_gpa" not in st.session_state:
    st.session_state.locked_gpa = None

# ======================================================
# GROUP BY SEMESTER
# ======================================================
semester_map = defaultdict(list)
for slot_code, slot in curriculum.items():
    semester = slot.get("semester")
    if semester is not None:
        semester_map[semester].append((slot_code, slot))

# ======================================================
# HELPERS
# ======================================================
def assign_elective(slot_code):
    selected = st.session_state.get(f"selectbox_{slot_code}", "—")
    if selected == "—":
        return
    chosen = next(
        (c for c in st.session_state.unassigned_courses if c["code"] == selected),
        None
    )
    if chosen is None:
        return
    chosen["assigned_slot"] = slot_code
    st.session_state.assignments.setdefault(slot_code, []).append(chosen)
    st.session_state.unassigned_courses.remove(chosen)

def get_or_create_planned(slot_code, slot):
    key = f"planned_{slot_code}"
    if key not in st.session_state:
        st.session_state[key] = {
            "code": slot_code,
            "name": slot.get("name", slot_code),
            "credits": slot.get("credits", 0),
            "grade": None,
            "planned": True
        }
    return st.session_state[key]

# ======================================================
# UI — CURRICULUM
# ======================================================
st.title(t("curriculum_title"))
st.divider()

for semester in sorted(semester_map.keys()):
    st.subheader(f"{semester}. {t('semester')}")
    st.divider()
    
    semester_total_credits = 0
    
    for slot_code, slot in semester_map[semester]:
        if slot.get("is_option_course") and not st.session_state.matching_confirmed:
            continue

        assigned = st.session_state.assignments.get(slot_code, [])
        slot_type = slot.get("type")
        
        col1, col2, col3, col4 = st.columns([2, 4, 1, 2])
        if assigned:
            latest = assigned[-1]
            col1.write(latest["code"])
            col2.write(latest.get("name", slot.get("name", slot_code)))
        else:
            col1.write(slot_code)
            col2.write(slot.get("name", slot_code))
        
        if assigned:
            col3.write(assigned[-1]["credits"])
        else:
            col3.write(slot.get("credits", ""))
        
        with col4:
            if slot_type in ("elective_slot", "free_elective", "departmental_elective"):
                if assigned:
                    latest = assigned[-1]
                    semester_total_credits += latest["credits"]
                    gcol, ucol = st.columns([3, 1])
                    
                    if st.session_state.matching_confirmed:
                        new_grade = gcol.selectbox(
                            t("grade"),
                            GRADE_OPTIONS,
                            index=GRADE_OPTIONS.index(latest["grade"]) if latest["grade"] in GRADE_OPTIONS else 0,
                            key=f"grade_edit_elective_{slot_code}",
                            label_visibility="collapsed"
                        )
                        latest["grade"] = new_grade
                    else:
                        gcol.success(latest["grade"])
                    
                    if ucol.button("↩️", key=f"undo_{slot_code}"):
                        removed = assigned.pop()
                        removed.pop("assigned_slot", None)
                        st.session_state.unassigned_courses.append(removed)
                        st.rerun()
                else:
                    options = ["—"] + sorted(
                        {c["code"] for c in st.session_state.unassigned_courses}
                    )
                    st.selectbox(
                        t("select_elective"),
                        options,
                        key=f"selectbox_{slot_code}",
                        label_visibility="collapsed",
                        on_change=assign_elective,
                        args=(slot_code,)
                    )
            else:
                if assigned:
                    latest = assigned[-1]
                    semester_total_credits += latest["credits"]
                    
                    if st.session_state.matching_confirmed:
                        new_grade = st.selectbox(
                            t("grade"),
                            GRADE_OPTIONS,
                            index=GRADE_OPTIONS.index(latest["grade"]) if latest["grade"] in GRADE_OPTIONS else 0,
                            key=f"grade_edit_{slot_code}",
                            label_visibility="collapsed"
                        )
                        latest["grade"] = new_grade
                    else:
                        st.success(latest["grade"])
                else:
                    if st.session_state.matching_confirmed:
                        planned = get_or_create_planned(slot_code, slot)
                        
                        # Sadece not girilmişse krediye dahil et
                        if planned["grade"] is not None and planned["grade"] != "—":
                            semester_total_credits += planned["credits"]

                        selected = st.selectbox(
                            t("grade"),
                            PLANNED_GRADE_OPTIONS,
                            index=0 if planned["grade"] is None else PLANNED_GRADE_OPTIONS.index(planned["grade"]),
                            key=f"planned_grade_{slot_code}",
                            label_visibility="collapsed"
                        )
                        planned["grade"] = None if selected == "—" else selected
                    else:
                        st.write("—")

    col_a, col_b = st.columns([3, 1])
    col_a.caption(t("total_credits_semester"))
    if semester_total_credits > SEMESTER_TARGET_CREDIT:
        col_b.success(f"{semester_total_credits} / 30 ({t('extra')})")
    elif semester_total_credits < SEMESTER_TARGET_CREDIT:
        col_b.warning(f"{semester_total_credits} / 30 ⚠️")
    else:
        col_b.info(f"{semester_total_credits} / 30")
    
    st.divider()

# ======================================================
# MÜFREDAT DIŞI DERSLER
# ======================================================
st.subheader(t("additional_courses"))
st.caption(t("additional_courses_caption"))

with st.expander(t("additional_courses_info_title")):
    st.markdown(t("additional_courses_info_text"))

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button(t("add_course")):
        st.session_state.mufredat_disi_slots.append(None)
    st.caption(t("add_course_hint"))

with col_btn2:
    if st.button(t("add_manual_course")):
        st.session_state.mufredat_disi_slots.append("MANUAL")
    st.caption(t("add_manual_course_hint"))

for i, slot in enumerate(st.session_state.mufredat_disi_slots):
    if slot is None:
        options = ["—"] + sorted(
            {c["code"] for c in st.session_state.unassigned_courses}
        )
        selected = st.selectbox(
            f"{t('additional_course')} {i+1}",
            options,
            key=f"mufredat_disi_select_{i}"
        )
        if selected != "—":
            chosen = next(
                (c for c in st.session_state.unassigned_courses if c["code"] == selected),
                None
            )
            if chosen is None:
                st.rerun()
            chosen["assigned_slot"] = "mufredat_disi"
            st.session_state.mufredat_disi_slots[i] = chosen
            st.session_state.assignments.setdefault(
                "mufredat_disi", []
            ).append(chosen)
            st.session_state.unassigned_courses.remove(chosen)
            st.rerun()
    elif slot == "MANUAL":
        # Manuel ders girişi formu
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        course_code = col1.text_input(
            t("course_code"),
            key=f"manual_code_{i}",
            placeholder="MATH 101",
            label_visibility="collapsed"
        )
        
        credits = col2.number_input(
            t("credits"),
            min_value=0,
            max_value=30,
            value=3,
            key=f"manual_credits_{i}",
            label_visibility="collapsed"
        )
        
        grade = col3.selectbox(
            t("grade"),
            GRADE_OPTIONS,
            key=f"manual_grade_{i}",
            label_visibility="collapsed"
        )
        
        if col4.button("✅", key=f"confirm_manual_{i}"):
            if course_code.strip():
                manual_course = {
                    "code": course_code.strip().upper(),
                    "name": course_code.strip().upper(),
                    "credits": credits,
                    "grade": grade,
                    "assigned_slot": "mufredat_disi",
                    "manual": True
                }
                st.session_state.mufredat_disi_slots[i] = manual_course
                st.session_state.assignments.setdefault(
                    "mufredat_disi", []
                ).append(manual_course)
                st.rerun()
            else:
                st.error(t("course_code_required"))
    else:
        course = slot
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        col1.markdown(f"**{course['code']}**")
        
        if st.session_state.matching_confirmed:
            new_grade = col2.selectbox(
                t("grade"),
                GRADE_OPTIONS,
                index=GRADE_OPTIONS.index(course["grade"]) if course["grade"] in GRADE_OPTIONS else 0,
                key=f"grade_edit_mufredat_{i}",
                label_visibility="collapsed"
            )
            course["grade"] = new_grade
        else:
            col2.markdown(course["grade"])
        
        col3.markdown(f"{course['credits']} cr")
        if col4.button("✖", key=f"remove_mufredat_{i}"):
            st.session_state.mufredat_disi_slots.pop(i)
            st.session_state.assignments["mufredat_disi"].remove(course)
            if not course.get("manual", False):
                course.pop("assigned_slot", None)
                st.session_state.unassigned_courses.append(course)
            st.rerun()

# ======================================================
# CONFIRM MATCHING
# ======================================================

st.divider()

if not st.session_state.matching_confirmed:
    if st.button(t("confirm_matching")):
        st.session_state.matching_confirmed = True

        included_courses = [
            c for courses in st.session_state.assignments.values() for c in courses
        ]
        
        planned_courses = [
            v for v in st.session_state.values()
            if isinstance(v, dict) and v.get("planned") and v.get("grade") is not None and v.get("grade") != "—"
        ]

        included_courses.extend(planned_courses)

        locked_gpa = calculate_gpa(included_courses, curriculum)
        st.session_state.locked_gpa = locked_gpa

        st.success(t("matching_confirmed_success"))
        st.rerun()
else:
    col1, col2 = st.columns([4, 1])
    col1.info(t("matching_locked"))
    if col2.button("🔓 " + t("unlock_matching")):
        st.session_state.matching_confirmed = False
        st.session_state.locked_gpa = None
        st.rerun()


# ======================================================
# GPA & TOTAL CREDITS
# ======================================================
included_courses = [
    c for courses in st.session_state.assignments.values() for c in courses
] + [
    v for v in st.session_state.values()
    if isinstance(v, dict) and v.get("planned") and v.get("grade") is not None and v.get("grade") != "—"
]

gpa = calculate_gpa(included_courses, curriculum)
total_credits = sum(c["credits"] for c in included_courses)

delta = None
if st.session_state.locked_gpa is not None:
    delta = gpa - st.session_state.locked_gpa

# ======================================================
# SIDEBAR — LIVE SUMMARY
# ======================================================
st.sidebar.markdown("---")
st.sidebar.subheader(t("current_summary"))
if delta is not None:
    st.sidebar.metric(
        t("gpa"),
        round(gpa, 2),
        delta=f"{delta:+.2f}"
    )
else:
    st.sidebar.metric(t("gpa"), round(gpa, 2))
st.sidebar.metric(t("total_credits"), total_credits)