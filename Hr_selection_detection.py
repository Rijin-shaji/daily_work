import json
import re
from datetime import datetime

INPUT_FILE = "step1_raw_text.json"
OUTPUT_FILE = "step2_sections.json"

HEADERS = [
    "skills","technical skills","competencies","expertise",
    "tools","technologies","projects","certifications",
    "experience","work experience","employment","work history",
    "education","languages",
    "summary","profile","objective","workshop"
]

SKILL_HEADERS = [
    "skills","technical skills","competencies","expertise","My Skills"
    "tools","technologies","projects","certifications"
]

EXP_HEADERS = [
    "experience","work experience","employment","work history","projects"
]

LANGUAGES = {
    "english", "hindi", "tamil", "malayalam",
    "french", "spanish", "german", "arabic", "urdu"
}

# FUNCTIONS
def split_sections(text):
    pattern = r'(?i)\b(' + '|'.join(HEADERS) + r')\b'
    matches = list(re.finditer(pattern, text))

    sections = {}
    for i, m in enumerate(matches):
        start = m.end()
        name = m.group(0).lower()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        sections[name] = text[start:end].strip()

    return sections

def combine_sections(sections, headers_list):
    combined = ""
    for h in headers_list:
        combined += sections.get(h.lower(), "") + " "
    return combined.strip()

#REMOVE LANGUAGES FROM SKILLS
def remove_languages_from_skills(skills_text):
    parts = re.split(r"[,\n•\-|]+", skills_text)
    clean = []
    for p in parts:
        p = p.strip()
        if p and p.lower() not in LANGUAGES:
            clean.append(p)
    return ", ".join(clean)

def extract_name(text, filename=""):
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    for line in lines[:15]:
        line = re.sub(r'\S+@\S+', '', line)
        line = re.sub(r'\+?\d[\d\- ]{8,}', '', line)
        line = re.sub(
            r'(?i)^(resume|cv|curriculum vitae|profile)[:\- ]*',
            '', line
        ).strip()

        words = line.split()
        if 1 < len(words) <= 6 and all(re.match(r"^[A-Za-z\.\-']+$", w) for w in words):
            return line.title()

    return filename.rsplit(".", 1)[0].title()

def extract_email(text):
    match = re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text)
    return match.group(0) if match else "Not found"

def extract_experience_from_section(experience_text):
    if not experience_text or not experience_text.strip():
        return {
            "experience_years": 0,
            "internship_years": 0,
            "total_experience_years": 0
        }

    blocks = re.split(r'\n{1,}', experience_text)

    experience_months = 0
    internship_months = 0

    DATE_PATTERN = re.compile(
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*(\d{4})'
        r'\s*(?:-|to)\s*'
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*(\d{4}|Present|Current|Now)',
        re.I
    )

    IT_KEYWORDS = [
        "software", "developer", "engineer", "data", "ai", "ml",
        "python", "java", "web", "cloud", "backend", "frontend"
    ]

    for block in blocks:
        block_lower = block.lower()
        matches = list(DATE_PATTERN.finditer(block))
        if not matches:
            continue

        is_internship = re.search(r'\bintern|internship|trainee\b', block_lower)
        is_it_relevant = any(k in block_lower for k in IT_KEYWORDS)

        for m in matches:
            sm, sy, em, ey = m.groups()
            try:
                start = datetime.strptime(f"{sm or 'Jan'} {sy}", "%b %Y")
                end = datetime.now() if ey.lower() in {"present", "current", "now"} \
                      else datetime.strptime(f"{em or 'Jan'} {ey}", "%b %Y")
            except:
                continue

            months = (end.year - start.year) * 12 + (end.month - start.month)
            if months <= 0:
                continue

            if is_internship:
                if months >= 1 and is_it_relevant:
                    internship_months += months
            else:
                experience_months += months

    return {
        "experience_years": round(experience_months / 12, 1),
        "internship_years": round(internship_months / 12, 1),
        "total_experience_years": round((experience_months + internship_months) / 12, 1)
    }

# MAIN
def run():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        resumes = json.load(f)

    results = []

    for r in resumes:
        text = r["raw_text"]
        sections = split_sections(text)

        raw_skills = combine_sections(sections, SKILL_HEADERS)
        skills = remove_languages_from_skills(raw_skills)
        experience_section = combine_sections(sections, EXP_HEADERS)
        experience_data = extract_experience_from_section(experience_section)

        results.append({
            "resume_id": r["resume_id"],
            "filename": r["filename"],
            "raw_text": text,
            "name": extract_name(text, r["filename"]),
            "email": extract_email(text),
            "skills": skills,
            "experience": experience_section
        })

        print("Processed:", r["filename"])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nSaved cleaned data to", OUTPUT_FILE)

if __name__ == "__main__":
    run()


