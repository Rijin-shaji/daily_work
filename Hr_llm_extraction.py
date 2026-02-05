import json
import re
import os
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

INPUT_FILE = "step2_sections.json"
OUTPUT_FILE = "step3_llm_output.json"
LLM_MODEL_NAME = "llama-3.3-70b-versatile"

# API Key check
api_key = os.getenv("GROQ_API")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable not set")

client = Groq(api_key=api_key)

PROMPT = """
Extract professional and technical skills from the following resume text.

Rules:
- Extract ONLY technical skills, tools, programming languages, frameworks, certifications
- Return short phrases (2-5 words maximum)
- NO full sentences
- NO job descriptions
- NO soft skills like "communication" or "teamwork"

Return ONLY a JSON array of skills (NO markdown, NO code blocks):
["skill1", "skill2", "skill3"]

Resume text:
"""

SKILLS_HEADERS = [
    "skills", "technical skills", "competencies", "expertise",
    "tools", "technologies", "projects", "certifications"
]


# FUNCTIONS
def combine_skill_sections(r):
    skills_text = ""
    for key, val in r.items():
        if any(sh in key.lower() for sh in SKILLS_HEADERS):
            skills_text += val + " "
    return skills_text.strip()


def extract_experience_details(text):
    if not text or not isinstance(text, str):
        return {
            "total_experience_years": 0,
            "work_experience_count": 0,
            "internship_count": 0
        }

    text = re.sub(r'(\d{4})([A-Za-z])', r'\1 \2', text)

    blocks = re.split(r'\n{2,}|(?:experience|employment|internship)', text, flags=re.I)

    work_months = 0
    internship_months = 0
    work_count = 0
    internship_count = 0

    date_pattern = re.compile(
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*(\d{4})'
        r'\s*(?:-|to)\s*'
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*(\d{4}|Present|Current|Now)',
        re.I
    )

    for block in blocks:
        block_lower = block.lower()
        match = date_pattern.search(block)

        if not match:
            continue

        sm, sy, em, ey = match.groups()

        try:
            start_date = datetime.strptime(f"{sm or 'Jan'} {sy}", "%b %Y")
            if ey.lower() in {"present", "current", "now"}:
                end_date = datetime.now()
            else:
                end_date = datetime.strptime(f"{em or 'Jan'} {ey}", "%b %Y")
        except:
            continue

        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        if months <= 0:
            continue

        if re.search(r'\bintern(ship)?\b', block_lower):
            internship_months += months
            internship_count += 1
        else:
            work_months += months
            work_count += 1

    return {
        "total_experience_years": round(work_months / 12, 1) if work_months else 0,
        "work_experience_count": work_count,
        "internship_count": internship_count
    }


# MAIN
def run():
    data = json.load(open(INPUT_FILE, encoding="utf-8"))
    results = []

    for r in data:
        final_name = r.get("name", "Unknown")
        final_email = r.get("email", "")
        print(f"Processing: {r['filename']}")
        print(f"  Name: {final_name}")
        print(f"  Email: {final_email}")

        skills_text = combine_skill_sections(r)
        if not skills_text.strip():
            skills_text = r.get("raw_text", "")[:2000]

        experience_text = r.get("experience_section", "")

        llm_input = f"{skills_text}\n\n{experience_text}"

        try:
            response = client.chat.completions.create(
                model=LLM_MODEL_NAME,
                messages=[{"role": "user", "content": PROMPT + llm_input}],
                temperature=0
            )

            content = response.choices[0].message.content.strip()

            if content.startswith("```"):
                content = re.sub(r'^```(?:json)?\n?', '', content)
                content = re.sub(r'\n?```$', '', content)

            skills_list = json.loads(content)

            if not isinstance(skills_list, list):
                skills_list = []

        except Exception as e:
            print(f"  ERROR extracting skills: {e}")
            skills_list = []

        exp_years = extract_experience_details(experience_text + " " + skills_text)

        final_result = {
            "name": final_name,
            "email": final_email,
            "skills": skills_list,
            "experience_years": exp_years
        }

        results.append({
            "resume_id": r["resume_id"],
            "filename": r["filename"],
            "extracted": final_result
        })

        print(f"  ✓ Skills: {len(skills_list)}, Experience: {exp_years} years")
        print()

    # Save results
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Complete! Saved to {OUTPUT_FILE}")
    print(f"  Total resumes processed: {len(results)}")


if __name__ == "__main__":
    run()




