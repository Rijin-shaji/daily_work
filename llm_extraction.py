import json
import re
import os
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

# ==============================
# LOAD ENV
# ==============================
load_dotenv()  # loads from .env if present

# ==============================
# CONFIG
# ==============================
INPUT_FILE = "step2_sections.json"
OUTPUT_FILE = "step3_llm_output.json"
LLM_MODEL_NAME = "llama-3.3-70b-versatile"

# API Key check
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable not set")

client = Groq(api_key=api_key)

PROMPT = """
Extract from this resume:

1) Full Name
2) Email
3) Skills (professional/technical only)

Rules:
- Skills must be short phrases, not sentences
- Return ONLY JSON
- Format:

{
  "name": "",
  "email": "",
  "skills": []
}

Resume:
"""

# Headers indicating skills sections
SKILLS_HEADERS = [
    "skills", "technical skills", "competencies", "expertise",
    "tools", "technologies", "projects", "certifications"
]

# -------------------------------
# FUNCTIONS
# -------------------------------

def combine_skill_sections(r):
    skills_text = ""
    for key, val in r.items():
        if any(sh in key.lower() for sh in SKILLS_HEADERS):
            skills_text += val + " "
    return skills_text.strip()

def fallback_email(raw_text):
    m = re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', raw_text)
    return m.group(0) if m else ""

def fallback_name(raw_text):
    lines = raw_text.split("\n")[:10]
    for line in lines:
        line = line.strip()
        if 1 < len(line.split()) <= 4 and all(c.isalpha() or c=='.' for c in line.replace("-", " ").split()):
            return line.title()
    return "Unknown"

def extract_experience_years(text):
    text = re.sub(r'(\d{4})([A-Za-z])', r'\1 \2', text)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    matches = re.findall(
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4})\s*(?:-|to)\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}|Present|Current|Now)?',
        text, flags=re.IGNORECASE
    )

    total_months = 0
    for start, end in matches:
        try:
            start = start.strip()
            start_date = datetime.strptime(start, "%b %Y") if any(m.isalpha() for m in start) else datetime.strptime(start, "%Y")
        except:
            continue

        try:
            if end is None or end.strip().lower() in ["present", "current", "now"]:
                end_date = datetime.now()
            else:
                end = end.strip()
                end_date = datetime.strptime(end, "%b %Y") if any(m.isalpha() for m in end) else datetime.strptime(end, "%Y")
        except:
            end_date = datetime.now()

        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        if months > 0:
            total_months += months

    return round(total_months / 12.0, 1)

# -------------------------------
# MAIN
# -------------------------------

def run():
    data = json.load(open(INPUT_FILE, encoding="utf-8"))
    results = []

    for r in data:
        raw_text = r.get("raw_text", "")

        skills_text = combine_skill_sections(r)
        if not skills_text.strip():
            skills_text = raw_text

        name_hint = r.get("name_guess", "Unknown")
        if name_hint == "Unknown":
            name_hint = fallback_name(raw_text)

        email_hint = r.get("email", "")
        if not email_hint or "@" not in email_hint:
            email_hint = fallback_email(raw_text)

        text_input = f"""
Name hint: {name_hint}
Email hint: {email_hint}

Skills + Technical Skills Section:
{skills_text}

Experience Section:
{r.get("experience_section","")}
"""

        response = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[{"role": "user", "content": PROMPT + text_input}],
            temperature=0
        )

        content = response.choices[0].message.content

        try:
            parsed = json.loads(content)
        except:
            parsed = {"raw_output": content}

        experience_text = r.get("experience_section", "") + " " + r.get("skills_section","")
        parsed["experience_years"] = extract_experience_years(experience_text)

        results.append({
            "resume_id": r["resume_id"],
            "filename": r["filename"],
            "extracted": parsed
        })

        print("Done:", r["filename"])

    json.dump(results, open(OUTPUT_FILE, "w", encoding="utf-8"), indent=2)
    print("LLM extraction complete, saved to", OUTPUT_FILE)

if __name__ == "__main__":
    run()




