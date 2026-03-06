import json

input_file = "step4_validated.json"
def split_text(text, chunk_size=300, overlap=50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks

with open(input_file, "r", encoding="utf-8") as f:
    resumes = json.load(f)


all_chunks = []

for resume in resumes:

    skills = " ".join(resume.get("skills", []))

    text = f"""
    Name: {resume.get("name","")}
    Skills: {skills}
    Experience: {resume.get("total_experience_years","")} years
    Internship: {resume.get("internship_years","")} years
    """

    chunks = split_text(text)

    for chunk in chunks:
        chunk_data = {
            "text": chunk,
            "resume_id": resume.get("resume_id"),
            "filename": resume.get("filename"),
            "file_path": resume.get("file_path")
        }

        all_chunks.append(chunk_data)

with open("step5_chunks.json", "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, indent=2)
print("Resumes processed:", len(resumes))
print("Chunks created:", len(all_chunks))