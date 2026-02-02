import os
import json
import faiss
import torch
import pdfplumber
import numpy as np
from tkinter import Tk, filedialog
from transformers import AutoTokenizer, AutoModel
from groq import Groq


# CONFIG
HF_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
FAISS_INDEX_FILE = "resume_faiss.index"
METADATA_FILE = "resume_metadata.json"
TOP_K = 5
MAX_TOKENS = 256
LLM_MODEL = "llama-3.3-70b-versatile"


# GROQ CLIENT
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not set")

llm_client = Groq(api_key=api_key)


# LOAD FAISS + METADATA
index = faiss.read_index(FAISS_INDEX_FILE)

with open(METADATA_FILE, "r", encoding="utf-8") as f:
    metadata_store = json.load(f)

print(f"FAISS vectors loaded : {index.ntotal}")
print(f"Metadata entries    : {len(metadata_store)}")

# LOAD EMBEDDING MODEL
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_NAME)
model = AutoModel.from_pretrained(HF_MODEL_NAME).to(device)
model.eval()

# UTILITY FUNCTIONS
def clean_text(text):
    return " ".join(text.split()).replace("\x00", "")

def extract_text_from_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return clean_text(text)

def embed_text(text):
    encoded = tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=MAX_TOKENS,
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        out = model(**encoded)
        tokens = out.last_hidden_state
        mask = encoded["attention_mask"].unsqueeze(-1).float()
        pooled = (tokens * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
        pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)

    return pooled.cpu().numpy().astype("float32")

def upload_pdf(title):
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(
        title=title,
        filetypes=[("PDF files", "*.pdf")]
    )
    root.destroy()
    return path


# FAISS SEARCH (NO LLM INTERFERENCE)
def search_faiss(vector, top_k=TOP_K):
    distances, indices = index.search(vector, top_k)
    results = []

    for idx, score in zip(indices[0], distances[0]):
        if idx >= len(metadata_store):
            continue

        entry = metadata_store[idx]
        meta = entry.get("metadata", {})

        results.append({
            "similarity_score": float(score),
            "resume_text": entry.get("text", ""),
            "metadata": meta,
            "filename": entry.get("filename", "Unknown")
        })

    return results


# JOB SEEKER LLM
def seeker_analysis(job_match):
    prompt = f"""
You are a career advisor.

Job Description:
{job_match["resume_text"]}

Provide:
1. Role Summary
2. Required Skills
3. Experience Level
4. Why this role suits the candidate

Be concise and factual.
"""

    response = llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a professional career advisor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=300
    )

    return response.choices[0].message.content

# HR LLM (EVALUATION ONLY)
def hr_evaluation(candidate, jd_text):
    meta = candidate["metadata"]

    prompt = f"""
You are an HR evaluator.

Job Description:
{jd_text}

Candidate Information (trusted):
Experience Years: {meta.get("experience_years")}
Skills: {", ".join(meta.get("skills", []))}

Resume Summary:
{candidate["resume_text"]}

Evaluate ONLY:
1. Candidate Summary
2. Strengths
3. Skill Gaps
4. Hiring Recommendation (Hire / Consider / Reject)

Do NOT invent facts.
"""

    response = llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a strict HR analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=400
    )

    return response.choices[0].message.content


# MAIN FLOW
def main():
    print("\nWho are you?")
    print("1. Job Seeker")
    print("2. HR / Recruiter")

    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        pdf_path = upload_pdf("Upload Resume PDF")
    elif choice == "2":
        pdf_path = upload_pdf("Upload Job Description PDF")
    else:
        print("Invalid choice")
        return

    if not pdf_path:
        print("No file selected")
        return

    text = extract_text_from_pdf(pdf_path)
    vector = embed_text(text)
    matches = search_faiss(vector)

    if not matches:
        print("No matches found")
        return

    # JOB SEEKER MODE
    if choice == "1":
        print("\n===== TOP JOB MATCHES =====\n")
        for i, match in enumerate(matches[:3], 1):
            print("=" * 60)
            print(f"MATCH #{i} | Score: {match['similarity_score']:.4f}\n")
            print(seeker_analysis(match))

    # HR MODE
    elif choice == "2":
        print("\n===== TOP CANDIDATES =====\n")
        for i, cand in enumerate(matches[:3], 1):
            meta = cand["metadata"]
            print("=" * 60)
            print(f"MATCH #{i} | Score: {cand['similarity_score']:.4f}")
            print(f"Resume File : {cand['filename']}")
            print(f"Experience  : {meta.get('experience_years')} years\n")
            print(hr_evaluation(cand, text))

# RUN
if __name__ == "__main__":
    main()




