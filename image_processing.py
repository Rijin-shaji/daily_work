import pytesseract
import cv2
import re
import json
import os
from groq import Groq
from dotenv import load_dotenv
import tkinter as tk
from tkinter import filedialog

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API"))

PROMPT = """
Extract ONLY technical skills from the text.

Rules:
- Only tools, technologies, programming languages
- Remove phrases like "experience in", "knowledge of"
- Return short names (1–3 words)
- No sentences

Return JSON array:
["skill1", "skill2"]

Text:
"""

def choose_image():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])

def extract_text(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bw = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    text = pytesseract.image_to_string(bw)
    return text

def extract_skills(text):
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": PROMPT + text[:2000]}],
            temperature=0
        )
        content = res.choices[0].message.content.strip()

        if content.startswith("```"):
            content = re.sub(r'^```(?:json)?\n?', '', content)
            content = re.sub(r'\n?```$', '', content)
        skills = json.loads(content)
        return list(set(skills))

    except:
        return []

def extract_email(text):
    match = re.findall(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+", text)
    return match[0] if match else "Not found"

def extract_phone(text):
    match = re.findall(r"\+?\d[\d\s\-]{8,15}", text)
    return match[0] if match else "Not found"

def extract_location(text):
    lines = text.split("\n")
    for line in lines:
        if "location" in line.lower():
            return line.split(":")[-1].strip()
    return "Not found"

def extract_experience(text):
    match = re.findall(r"\d+\s*(?:\+)?\s*(?:years?|yrs?)", text.lower())
    return match[0] if match else "Not found"

def extract_role(text):
    keywords = ["engineer", "developer", "analyst", "scientist", "intern"]
    for line in text.split("\n"):
        if any(k in line.lower() for k in keywords):
            return line.strip()
    return "Not found"

def extract_company(text):
    lines = text.split("\n")
    for line in lines[:5]:  # usually top
        if len(line.strip()) > 2:
            return line.strip()
    return "Not found"

def main():
    file_path = choose_image()

    if not file_path:
        print("No file selected")
        return

    text = extract_text(file_path)
    print("\n--- Extracted Text ---\n")
    print(text)

    details = {
        "Company": extract_company(text),
        "Role": extract_role(text),
        "Location": extract_location(text),
        "Email": extract_email(text),
        "Phone": extract_phone(text),
        "Experience": extract_experience(text),
        "Skills": extract_skills(text)
    }
    print("\n--- Job Details ---\n")
    for k, v in details.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()