import requests, os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env file")
else:
    r = requests.get(f"https://generativelanguage.googleapis.com/v1/models?key={api_key}")
    print(r.json())
