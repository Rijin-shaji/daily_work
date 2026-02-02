import json
import re

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
    "skills","technical skills","competencies","expertise",
    "tools","technologies","projects","certifications"
]

EXP_HEADERS = [
    "experience","work experience","employment","work history","projects"
]

# ==========================
# NEW: LANGUAGE BLOCKLIST
# ==========================
LANGUAGES = {
    "english", "hindi", "tamil", "malayalam", "malayala",
    "french", "spanish", "german", "arabic", "urdu"
}

# ==========================
# FUNCTIONS
# ==========================
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

# ==========================
# NEW: REMOVE LANGUAGES FROM SKILLS
# ==========================
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

# ==========================
# MAIN
# ==========================
def run():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        resumes = json.load(f)

    results = []

    for r in resumes:
        text = r["raw_text"]
        sections = split_sections(text)

        raw_skills = combine_sections(sections, SKILL_HEADERS)
        skills = remove_languages_from_skills(raw_skills)
        experience = combine_sections(sections, EXP_HEADERS)

        results.append({
            "resume_id": r["resume_id"],
            "filename": r["filename"],
            "raw_text": text,
            "name": extract_name(text, r["filename"]),
            "email": extract_email(text),
            "skills": skills,
            "experience_section": experience
        })

        print("Processed:", r["filename"])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nSaved cleaned data to", OUTPUT_FILE)

if __name__ == "__main__":
    run()


