import os
import requests
import urllib.parse
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

# --- Generate text with Gemini ---
def generate_content(prompt_text: str, mode="text"):
    if not GOOGLE_API_KEY:
        return "Error: GOOGLE_API_KEY not set in .env."

    try:
        model = "models/gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent"

        headers = {"Content-Type": "application/json"}
        params = {"key": GOOGLE_API_KEY}
        payload = {"contents": [{"parts": [{"text": prompt_text}]}]}

        resp = requests.post(url, headers=headers, params=params, json=payload, timeout=30)
        if resp.status_code == 200:
            js = resp.json()
            return js["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Error: API returned {resp.status_code} - {resp.text}"

    except Exception as e:
        return f"Error calling Gemini API: {e}"

# --- YouTube video link generator ---
def get_video_link(user_input: str):
    q = urllib.parse.quote_plus(user_input)
    return f"https://www.youtube.com/results?search_query={q}"

# --- Image link generator (Pixabay) ---
def get_image_link(prompt_text: str):
    if not PIXABAY_API_KEY:
        return "Error: PIXABAY_API_KEY not set."

    try:
        url = "https://pixabay.com/api/"
        params = {
            "key": PIXABAY_API_KEY,
            "q": prompt_text,
            "image_type": "photo",
            "safesearch": "true",
            "per_page": 3
        }
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        js = r.json()
        hits = js.get("hits", [])
        if hits:
            return hits[0].get("largeImageURL") or hits[0].get("webformatURL")
        else:
            return "No image found for your prompt."
    except Exception as e:
        return f"Error fetching image: {e}"
