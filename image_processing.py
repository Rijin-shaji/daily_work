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
    emoji_match = re.search(r"[📍📌🌍🗺️]\s*(.+?)(?:\||$)", text)
    if emoji_match:
        location = emoji_match.group(1).strip()
        location = re.sub(r"\s*\|.*", "", location)
        location = re.sub(r"\s*📱.*", "", location)
        location = re.sub(r"\+?\d+[\d\s\-().]*", "", location)
        location = re.sub(r"\s+", " ", location).strip()
        if location and len(location) > 2:
            return location
    for i, line in enumerate(lines):
        if re.search(r"(?:location|address)[\s:]+", line, re.IGNORECASE):
            if ":" in line:
                location = line.split(":")[-1].strip()
            else:
                location = line.replace("LOCATION", "").replace("location", "").replace("ADDRESS", "").replace(
                    "address", "").strip()
            if not location and i + 1 < len(lines):
                location = lines[i + 1].strip()
            location = re.sub(r"\+?\d+[\d\s\-().]*", "", location)
            location = re.sub(r"www\..*", "", location)
            location = re.sub(r"\s+", " ", location).strip()
            if location and len(location) > 2:
                return location
    city_pattern = r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
    match = re.search(city_pattern, text)
    if match:
        location = f"{match.group(1)}, {match.group(2)}"
        if "://" not in location and "@" not in location:
            return location
    return "Unknown"


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
    website_patterns = [
        r"www\.([a-zA-Z0-9\-]+)\.com",
        r"www\.([a-zA-Z0-9\-]+)\.co\.uk",
        r"www\.([a-zA-Z0-9\-]+)\.in",
        r"www\.([a-zA-Z0-9\-]+)\.org",
        r"www\.([a-zA-Z0-9\-]+)\.io",
        r"https?://(?:www\.)?([a-zA-Z0-9\-]+)\.",
    ]
    for pattern in website_patterns:
        website = re.search(pattern, text, re.IGNORECASE)
        if website:
            company_name = website.group(1).upper()
            return company_name
    email_match = re.search(r"@([a-zA-Z0-9\-]+)\.", text, re.IGNORECASE)
    if email_match:
        company_domain = email_match.group(1)
        generic_domains = ['gmail', 'yahoo', 'hotmail', 'outlook', 'protonmail']
        if company_domain.lower() not in generic_domains:
            return company_domain.upper()
    return "Unknown"

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