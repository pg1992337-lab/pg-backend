import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS Middleware - যেকোনো ডোমেইন থেকে রিকোয়েস্ট অ্যালাউ করবে
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"status": "Backend running"}

@app.post("/chat")
def chat(req: ChatRequest):
    if not GEMINI_API_KEY:
        return {"speech_response": "Error: GEMINI_API_KEY পাওয়া যায়নি। Render-এর Environment Variable চেক করুন।"}

    prompt_text = f"You are PG AI Assistant. Reply concisely in 1-2 short Bengali sentences to: {req.message}"

    # Google Gemini 2.5 REST Endpoint
    candidate_models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash-latest"
    ]

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}]
    }

    last_error = ""

    for model_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=12)
            res_data = res.json()

            if res.status_code == 200:
                text = res_data['candidates'][0]['content']['parts'][0]['text']
                return {"speech_response": text}
            else:
                last_error = res_data.get('error', {}).get('message', f"Status {res.status_code}")
        except Exception as err:
            last_error = str(err)

    return {"speech_response": f"API Error: {last_error}"}
