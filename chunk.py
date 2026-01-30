import json
import os
import textwrap

# ==============================
# CONFIG
# ==============================
VALIDATED_JSON = "step4_validated.json"
OUTPUT_CHUNKS_JSON = "step5_chunks.json"
CHUNK_SIZE = 250  # Max words per chunk

# Optional: you can split by sentences too
def split_text_into_chunks(text, chunk_size=CHUNK_SIZE):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

def run():
    if not os.path.exists(VALIDATED_JSON):
        print(f"Error: {VALIDATED_JSON} not found!")
        return

    with open(VALIDATED_JSON, "r", encoding="utf-8") as f:
        resumes = json.load(f)

    all_chunks = []

    for r in resumes:
        # Combine skills + experience section
        skills_text = ", ".join(r.get("skills", []))
        exp_text = r.get("experience_section", "")
        combined_text = (skills_text + " " + exp_text).strip()

        if not combined_text:
            continue  # Skip empty resumes

        # Split into chunks if needed
        chunks = split_text_into_chunks(combined_text)

        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "filename": r.get("filename", ""),
                "resume_id": r.get("resume_id", "")
            })

        print(f"Processed {r.get('filename', '')}, {len(chunks)} chunk(s)")

    # Save chunks JSON
    with open(OUTPUT_CHUNKS_JSON, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Saved {len(all_chunks)} chunks to {OUTPUT_CHUNKS_JSON}")

if __name__ == "__main__":
    run()

