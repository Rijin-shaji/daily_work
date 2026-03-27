import requests

post_id = "48abd1c8-610e-428c-b3cd-d8924336b094"
url = f"https://coderzonjobportal.up.railway.app/api/job-news/{post_id}"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Error: {response.status_code}")