import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

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
        return {"speech_response": "Error: GEMINI_API_KEY missing in Render environment variable."}

    prompt_text = f"You are PG AI Assistant. Reply concisely in 1-2 short Bengali sentences to: {req.message}"

    # Google-এর নতুন API Endpoint (gemini-2.5-flash)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}]
    }

    try:
        res = requests.post(url, json=payload, headers=headers)
        res_data = res.json()

        if res.status_code == 200:
            text = res_data['candidates'][0]['content']['parts'][0]['text']
            return {"speech_response": text}
        else:
            error_msg = res_data.get('error', {}).get('message', 'Unknown Error')
            return {"speech_response": f"API Error ({res.status_code}): {error_msg}"}

    except Exception as err:
        return {"speech_response": f"Server Error: {str(err)}"}
