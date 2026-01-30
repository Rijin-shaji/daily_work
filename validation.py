import json
import re

INPUT_FILE = "step3_llm_output.json"
OUTPUT_FILE = "step4_validated.json"

def clean_raw_output(raw_text):
    raw_text = raw_text.replace("```","").strip()
    try:
        return json.loads(raw_text)
    except:
        return {"raw_output": raw_text}

def validate_email(email):
    m = re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', email)
    return m.group(0) if m else "Not found"

def clean_skills(skills):
    clean = []
    for s in skills:
        s = s.strip().strip(",.;:")
        if s:
            clean.append(s)
    return list(set(clean))  # remove duplicates

def validate_experience(exp):
    try:
        exp = float(exp)
        return min(max(exp, 0), 40)
    except:
        return 0

data = json.load(open(INPUT_FILE,"r",encoding="utf-8"))
results = []

for r in data:
    extracted = clean_raw_output(r.get("extracted", {}).get("raw_output","{}"))

    name = extracted.get("name","Unknown")
    email = validate_email(extracted.get("email",""))
    skills = clean_skills(extracted.get("skills",[]))
    exp = validate_experience(extracted.get("experience_years",0))

    results.append({
        "resume_id": r["resume_id"],
        "filename": r["filename"],
        "name": name,
        "email": email,
        "skills": skills,
        "experience_years": exp
    })

json.dump(results, open(OUTPUT_FILE,"w",encoding="utf-8"), indent=2)
print("Validation complete, saved to",OUTPUT_FILE)
