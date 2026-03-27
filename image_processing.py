import pytesseract
import cv2
import re
import json
import os
import requests
import numpy as np
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API"))

post_id = "7f5ebf1c-30b2-4d7e-83f2-464afdfb7353"
url = f"https://coderzonjobportal.up.railway.app/api/job-news/{post_id}"

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
def extract_text_from_url(image_url):
    try:
        response = requests.get(image_url)
        if response.status_code != 200:
            print(" Failed to fetch image")
            return ""
        img_array = np.frombuffer(response.content, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            print(" Error decoding image")
            return ""

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        bw = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        text = pytesseract.image_to_string(bw)
        return text

    except Exception as e:
        print(" Image processing error:", e)
        return ""
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

    except json.JSONDecodeError:
        print(" JSON parsing error")
        return []
    except Exception as e:
        print(" Skill extraction error:", e)
        return []
def extract_email(text):
    match = re.findall(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+", text)
    return match[0] if match else "Not found"

def extract_phone(text):
    matches = re.findall(r"\+?\d[\d\s\-]{8,15}", text)
    phones = []
    for m in matches:
        clean = re.sub(r"\s+", "", m)
        if 10 <= len(clean) <= 15:
            phones.append(clean)
    if phones:
        return list(set(phones))
    return None

def extract_experience(text):
    match = re.findall(r"\d+\s*(?:\+)?\s*(?:years?|yrs?)", text.lower())
    return match[0] if match else "Not found"

def extract_role(text, job_data):
    api_role = job_data.get("title")
    if api_role and api_role.strip():
        role = api_role.strip()
        role = re.sub(r"[^\w\s]", "", role)
        role = re.sub(r"\s+", " ", role)
        role = re.sub(r"\bInterns\b", "Intern", role, flags=re.IGNORECASE)
        return role
    lines = text.split("\n")
    role_patterns = [
        r"(?:Role|Position|Job Title)\s*[:\-]\s*([A-Za-z\s!]+)",
        r"([A-Z][a-zA-Z\s]+Interns?)"
    ]
    for line in lines:
        for pattern in role_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                role = match.group(1).strip()
                role = re.sub(r"[^\w\s]", "", role)
                role = re.sub(r"\s+", " ", role)
                role = re.sub(r"\bInterns\b", "Intern", role, flags=re.IGNORECASE)
                if len(role) > 2:
                    return role
    return None

def extract_location(text, job_data):
    api_location = job_data.get("location")
    if api_location and api_location.strip():
        return api_location.strip()
    lines = text.split("\n")
    emoji_match = re.search(r"[📍📌🌍🗺️🔹🌐]\s*(.+?)(?:\||$)", text)
    if emoji_match:
        location = emoji_match.group(1).strip()
        location = re.sub(r"\s*\|.*", "", location)
        location = re.sub(r"\+?\d+[\d\s\-().]*", "", location)
        location = re.sub(r"\s+", " ", location).strip()
        if (
            "@" not in location and
            "http" not in location and
            len(location) > 2
        ):
            return location
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
        if "/" in clean_line or "|" in clean_line:
            if (
                "@" in clean_line or
                "http" in clean_line or
                any(char.isdigit() for char in clean_line) or
                len(clean_line.split()) > 6 or
                len(clean_line) < 5
            ):
                continue
            if clean_line.upper() == clean_line:
                return clean_line
    city_pattern = r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
    match = re.search(city_pattern, text)
    if match:
        location = f"{match.group(1)}, {match.group(2)}"
        if "@" not in location and "http" not in location:
            return location
    return None

def extract_company(text, job_data):
    api_company = None
    if job_data.get("company") and job_data["company"].get("name"):
        api_company = job_data["company"]["name"]
    elif job_data.get("companyName"):
        api_company = job_data.get("companyName")
    if api_company and api_company.strip():
        return api_company.strip()
    website_patterns = [
        r"www\.([a-zA-Z0-9\-]+)\.com",
        r"www\.([a-zA-Z0-9\-]+)\.co\.uk",
        r"www\.([a-zA-Z0-9\-]+)\.in",
        r"www\.([a-zA-Z0-9\-]+)\.org",
        r"www\.([a-zA-Z0-9\-]+)\.io",
        r"https?://(?:www\.)?([a-zA-Z0-9\-]+)\."
    ]
    for pattern in website_patterns:
        website = re.search(pattern, text, re.IGNORECASE)
        if website:
            return website.group(1).upper()
    email_match = re.search(r"@([a-zA-Z0-9\-]+)\.", text, re.IGNORECASE)
    if email_match:
        company_domain = email_match.group(1)
        generic_domains = ['gmail', 'yahoo', 'hotmail', 'outlook', 'protonmail']
        if company_domain.lower() not in generic_domains:
            return company_domain.upper()
    return None

def main():
    try:
        res = requests.get(url)
        if res.status_code != 200:
            print(" API Error:", res.status_code)
            return

        response_json = res.json()

        print("\n API details \n")
        print(response_json)
        job_data = response_json.get("data", {})
        image_url = job_data.get("poster")

        if not image_url:
            print(" No image in API")
            return
        print("\n Image URL:", image_url)
        text = extract_text_from_url(image_url)

        if not text.strip():
            print(" No details are in the poster ")
            return

        print("\n  Job Details \n")
        print(text)
        print("\n  Company Details \n")
        details = {
            "Company": extract_company(text,job_data),
            "Role": extract_role(text,job_data),
            "Location": extract_location(text,job_data),
            "Email": extract_email(text),
            "Phone": extract_phone(text),
            "Experience": extract_experience(text),
            "Skills": extract_skills(text),
        }
        for k, v in details.items():
            print(f"{k}: {v}")
    except Exception as e:
        print("  Error Occur ", e)
if __name__ == "__main__":
    main()