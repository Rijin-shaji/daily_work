import os
import json
import faiss
import torch
import numpy as np
import pdfplumber
from tkinter import Tk, filedialog
from transformers import AutoTokenizer, AutoModel

# ==========================
# CONFIG
# ==========================
HF_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 5
FAISS_INDEX_FILE = "resume_faiss.index"
METADATA_FILE = "resume_metadata.json"
MAX_TOKENS = 256

# ==========================
# LOAD FAISS & METADATA
# ==========================
index = faiss.read_index(FAISS_INDEX_FILE)

with open(METADATA_FILE, "r", encoding="utf-8") as f:
    metadata_store = json.load(f)

print(f"FAISS loaded: {index.ntotal} vectors")
print(f"Metadata loaded: {len(metadata_store)} entries")

# ==========================
# LOAD MODEL
# ==========================
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_NAME)
model = AutoModel.from_pretrained(HF_MODEL_NAME).to(device)
model.eval()

# ==========================
# FUNCTIONS
# ==========================
def clean_text(text):
    return " ".join(text.split()).replace("\x00", "")

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
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
        output = model(**encoded)

        token_embeddings = output.last_hidden_state
        mask = encoded["attention_mask"].unsqueeze(-1).expand(token_embeddings.size()).float()

        pooled = (token_embeddings * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
        pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)

    return pooled.cpu().numpy().astype("float32")

def upload_pdf(title="Select PDF"):
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    path = filedialog.askopenfilename(
        title=title,
        filetypes=[("PDF files", "*.pdf")]
    )

    root.destroy()
    return path

# ==========================
# FIXED SEARCH FUNCTION
# ==========================
def search_faiss(vector, top_k=TOP_K):
    distances, indices = index.search(vector, top_k)

    results = []

    for idx, dist in zip(indices[0], distances[0]):

        if idx >= len(metadata_store):
            continue

        entry = metadata_store[idx]

        # 🔥 IMPORTANT FIX: read nested metadata
        meta = entry.get("metadata", {})

        results.append({
            "similarity_score": float(dist),
            "name": meta.get("name", "Unknown"),
            "email": meta.get("email", "Unknown"),
            "skills": meta.get("skills", []),
            "experience_years": meta.get("experience_years", 0.0),
            "filename": entry.get("filename", "Unknown")
        })

    return results

# ==========================
# MAIN PIPELINE
# ==========================
def find_best_employees():
    print("\nUpload Job Description PDF...")
    jd_path = upload_pdf("Select Job Description PDF")

    if not jd_path:
        print("No file selected")
        return []

    print(f"JD uploaded: {os.path.basename(jd_path)}")

    jd_text = extract_text_from_pdf(jd_path)

    if not jd_text.strip():
        print("JD is empty")
        return []

    jd_vector = embed_text(jd_text)

    return search_faiss(jd_vector)

# ==========================
# RUN
# ==========================
if __name__ == "__main__":
    employees = find_best_employees()

    if employees:
        print("\n===== TOP MATCHED EMPLOYEES =====\n")

        for rank, emp in enumerate(employees, 1):
            print(f"Rank {rank}:")
            print(f"  Name             : {emp['name']}")
            print(f"  Email            : {emp['email']}")
            print(f"  Skills           : {', '.join(emp['skills'])}")
            print(f"  Experience Years : {emp['experience_years']}")
            print(f"  Resume File      : {emp['filename']}")
            print(f"  Similarity Score : {emp['similarity_score']:.4f}\n")


