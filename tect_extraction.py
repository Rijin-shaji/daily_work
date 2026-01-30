import os
import json
import re
import pdfplumber

# ==============================
# CONFIG
# ==============================
RESUME_FOLDER = "D:/project_2_resumes"
OUTPUT_FILE = "step1_raw_text.json"



# CLEANING

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\x00', '')
    return text.strip()



# PDF TEXT EXTRACTION

def extract_from_pdf(path):
    full_text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    full_text += t + "\n"
    except Exception as e:
        print(f"Error reading {path}: {e}")
    return full_text



# MAIN

def run():
    all_resumes = []

    if not os.path.exists(RESUME_FOLDER):
        print("Folder not found!")
        return

    files = [f for f in os.listdir(RESUME_FOLDER)
             if f.lower().endswith((".pdf", ".txt"))]

    print(f"Found {len(files)} resumes")

    for i, file in enumerate(files):
        path = os.path.join(RESUME_FOLDER, file)

        # Read file
        if file.lower().endswith(".pdf"):
            raw_text = extract_from_pdf(path)
        else:
            with open(path, "r", errors="ignore", encoding="utf-8") as f:
                raw_text = f.read()

        cleaned = clean_text(raw_text)

        if not cleaned:
            continue

        all_resumes.append({
            "resume_id": f"RES_{i}",
            "filename": file,
            "raw_text": cleaned
        })

        print(f"[{i+1}/{len(files)}] Extracted {file}")

    # Save output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_resumes, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run()

