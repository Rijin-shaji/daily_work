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


def split_sections(text):
    pattern = r'(?i)\b(' + '|'.join(HEADERS) + r')\b'
    matches = list(re.finditer(pattern, text))

    sections = {}

    for i, m in enumerate(matches):
        start = m.end()
        name = m.group(0).lower()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        content = text[start:end].strip()
        sections[name] = content

    return sections

def combine_sections(sections, headers_list):
    combined = ""
    for h in headers_list:
        combined += sections.get(h.lower(), "") + " "
    return combined.strip()

def extract_name(text, filename=""):
    lines = [L.strip() for L in text.split("\n") if L.strip() and len(L.strip()) > 2]

    for line in lines[:15]:
        # Remove emails and phone numbers
        line_clean = re.sub(r'\S+@\S+', '', line)
        line_clean = re.sub(r'\+?\d[\d\- ]{8,}', '', line_clean).strip()
        # Remove common prefixes
        line_clean = re.sub(r'(?i)^(resume|cv|curriculum vitae|of|profile|curriculum|vitae)[:\- ]*', '', line_clean).strip()

        words = line_clean.split()
        if 1 < len(words) <= 6:
            # Check each word: letters, dot, hyphen, apostrophe
            if all(re.match(r"^[A-Za-z\.\-']+$", w) for w in words):
                return line_clean.title()


    return filename.rsplit(".", 1)[0].title()


def extract_email(text):
    e = re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text)
    return e.group(0) if e else "Not found"


# Main

def run():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        resumes = json.load(f)

    results = []

    for r in resumes:
        text = r["raw_text"]
        sections = split_sections(text)

        skills = combine_sections(sections, SKILL_HEADERS)
        experience = combine_sections(sections, EXP_HEADERS)

        results.append({
            "resume_id": r["resume_id"],
            "filename": r["filename"],
            "raw_text": text,  # raw_text for LLaMA fallback
            "name_guess": extract_name(text),
            "email": extract_email(text),
            "skills_section": skills,
            "experience_section": experience
        })

        print("Processed", r["filename"])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nSaved to", OUTPUT_FILE)

if __name__ == "__main__":
    run()

