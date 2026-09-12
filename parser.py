import re
from typing import List, Tuple
import pdfplumber
from models import Course


def extract_student_id(text: str) -> str:
    match = re.search(r"Student\s*ID\s*[:#]?\s*([A-Z0-9-]+)", text, re.IGNORECASE)
    return match.group(1).strip() if match else "STU-1001"


def extract_courses_from_text(text: str) -> List[Course]:
    courses = []
    seen = set()

    pattern = re.compile(
        r"([A-Z]{2,4}\s*\d{3,4})\s+([A-Za-z0-9\s,\-\&]+?)\s+(\d)\s+(?:[A-D][+-]?|F|P|CR|PASS)",
        re.MULTILINE
    )

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        match = pattern.search(line)
        if match:
            code = match.group(1).replace(" ", "").upper()
            title = match.group(2).strip()
            credits = int(match.group(3))

            if code not in seen:
                seen.add(code)
                courses.append(Course(course_code=code, title=title, credits=credits, schedule=[]))
            continue

        simple_match = re.search(r"\b([A-Z]{2,4}\s*\d{3,4})\b", line)
        credits_match = re.search(r"\b([1-6])\s*(?:credits?|cr|hrs)?\b", line, re.IGNORECASE)
        if simple_match and credits_match:
            code = simple_match.group(1).replace(" ", "").upper()
            if code not in seen:
                seen.add(code)
                courses.append(Course(
                    course_code=code,
                    title=f"Course {code}",
                    credits=int(credits_match.group(1)),
                    schedule=[]
                ))

    return courses


def parse_transcript(pdf_path: str) -> Tuple[str, List[Course]]:
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for p in pdf.pages:
            txt = p.extract_text()
            if txt:
                pages.append(txt)

    full_text = "\n".join(pages)
    student_id = extract_student_id(full_text)
    completed_courses = extract_courses_from_text(full_text)

    return student_id, completed_courses
