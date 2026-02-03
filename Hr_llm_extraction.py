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

# Simplified prompt - ONLY for skills extraction
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

# Headers indicating skills sections
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
            start_date = datetime.strptime(start, "%b %Y") if any(m.isalpha() for m in start) else datetime.strptime(
                start, "%Y")
        except:
            continue

        try:
            if end is None or end.strip().lower() in ["present", "current", "now"]:
                end_date = datetime.now()
            else:
                end = end.strip()
                end_date = datetime.strptime(end, "%b %Y") if any(m.isalpha() for m in end) else datetime.strptime(end,
                                                                                                                   "%Y")
        except:
            end_date = datetime.now()

        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        if months > 0:
            total_months += months

    return round(total_months / 12.0, 1)


# MAIN
def run():
    data = json.load(open(INPUT_FILE, encoding="utf-8"))
    results = []

    for r in data:
        # DIRECTLY take name and email from JSON - that's it!
        final_name = r.get("name", "Unknown")
        final_email = r.get("email", "")

        print(f"Processing: {r['filename']}")
        print(f"  Name: {final_name}")
        print(f"  Email: {final_email}")

        # Combine skills text for LLM
        skills_text = combine_skill_sections(r)
        if not skills_text.strip():
            skills_text = r.get("raw_text", "")[:2000]

        experience_text = r.get("experience_section", "")

        # Create input for LLM - ONLY for skills extraction
        llm_input = f"{skills_text}\n\n{experience_text}"

        # Call LLM ONLY for skills
        try:
            response = client.chat.completions.create(
                model=LLM_MODEL_NAME,
                messages=[{"role": "user", "content": PROMPT + llm_input}],
                temperature=0
            )

            content = response.choices[0].message.content.strip()

            # Remove markdown if present
            if content.startswith("```"):
                content = re.sub(r'^```(?:json)?\n?', '', content)
                content = re.sub(r'\n?```$', '', content)

            skills_list = json.loads(content)

            # Ensure it's a list
            if not isinstance(skills_list, list):
                skills_list = []

        except Exception as e:
            print(f"  ERROR extracting skills: {e}")
            skills_list = []

        # Calculate experience years
        exp_years = extract_experience_years(experience_text + " " + skills_text)

        # Build final result - name and email directly from JSON
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




