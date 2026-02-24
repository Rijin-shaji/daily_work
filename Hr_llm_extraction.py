import json
import re
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

INPUT_FILE = "step2_sections.json"
OUTPUT_FILE = "step3_llm_output.json"
LLM_MODEL_NAME = "llama-3.3-70b-versatile"

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


def combine_skill_sections(r):
    skills_text = ""
    for key, val in r.items():
        if any(sh in key.lower() for sh in SKILLS_HEADERS):
            skills_text += val + " "
    return skills_text.strip()


def run():
    data = json.load(open(INPUT_FILE, encoding="utf-8"))
    results = []

    for r in data:
        final_name = r.get("name", "Unknown")
        final_email = r.get("email", "")

        print(f"Processing: {r['filename']}")
        print(f"  Name: {final_name}")
        print(f"  Email: {final_email}")

        # Get skills text for LLM
        skills_text = combine_skill_sections(r)
        if not skills_text.strip():
            skills_text = r.get("raw_text", "")[:2000]

        experience_section = r.get("experience_section", "")
        llm_input = f"{skills_text}\n\n{experience_section}"

        # Extract skills using LLM
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

        experience_years = r.get("experience_years", 0.0)
        internship_years = r.get("internship_years", 0.0)
        total_experience_years = r.get("total_experience_years", 0.0)

        final_result = {
            "name": final_name,
            "email": final_email,
            "skills": skills_list,
            "experience_years": experience_years,
            "internship_years": internship_years,
            "total_experience_years": total_experience_years
        }

        results.append({
            "resume_id": r["resume_id"],
            "filename": r["filename"],
            "extracted": final_result
        })

        print(f"  Skills: {len(skills_list)}")
        print(f"  Experience: {total_experience_years} years\n")

    # Save results
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nComplete! Saved to {OUTPUT_FILE}")
    print(f"  Total resumes processed: {len(results)}")


if __name__ == "__main__":
    run()



