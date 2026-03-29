import requests

url = f"https://coderzonjobportal.up.railway.app/api/job-news?page=1&limit=20"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Error: {response.status_code}")