import pdfplumber
import re
import json
import unicodedata


# ---------- PDF → TEXT ----------
import pdfplumber
from io import BytesIO

def extract_text_from_pdf(uploaded_file):
    if uploaded_file is None:
        return ""

    pdf_bytes = BytesIO(uploaded_file.read())

    with pdfplumber.open(pdf_bytes) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""

    return text

# ---------- COURSE REGEX ----------
COURSE_PATTERN = re.compile(
    r"""
    (?P<code>[A-Zİİ]{2,6}\s?\d{3}[A-Z]?\*?)
    \s+
    (?P<name>.+?)
    \s+
    (?P<credits>\d+)
    \s+
    (?P<grade>A-|A|B\+|B-|B|C\+|C-|C|D\+|D|F|S)
    """,
    re.VERBOSE
)


# ---------- TEXT → COURSE LIST ----------
def parse_courses_from_text(text):
    courses_dict = {}

    for match in COURSE_PATTERN.finditer(text):
        raw_code = match.group("code")

        # ---- CODE NORMALIZATION ----
        code = (
            raw_code
            .replace("*", "")
            .replace("\u00a0", " ")
            .strip()
        )

        code = unicodedata.normalize("NFKD", code)
        code = re.sub(r"I[\u0307]*", "I", code)
        code = re.sub(r"\s+", " ", code)
        code = code.upper()

        course = {
            "code": code,
            "name": match.group("name").strip(),
            "credits": int(match.group("credits")),
            "grade": match.group("grade"),
            "assigned_slot": None
        }

        # aynı ders birden fazla alınmışsa SONUNCU kalsın
        courses_dict[code] = course

    return list(courses_dict.values())


# ---------- PDF → COURSES (TEK ADIM) ----------
def parse_transcript_pdf(file):
    """
    Streamlit için ana giriş noktası
    PDF upload → list[course]
    """
    text = extract_text_from_pdf(file)
    return parse_courses_from_text(text)


# ---------- CLI KULLANIM (OPSİYONEL) ----------
if __name__ == "__main__":
    with open("transcript.pdf", "rb") as f:
        courses = parse_transcript_pdf(f)

    with open("parsed_transcript.json", "w", encoding="utf-8") as out:
        json.dump(courses, out, indent=2, ensure_ascii=False)

    print(f"✅ Toplam ders: {len(courses)}")