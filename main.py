import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"status": "Backend running"}

@app.post("/chat")
def chat(req: ChatRequest):
    prompt_text = f"You are PG AI Assistant. Reply concisely in 1-2 short Bengali sentences to: {req.message}"
    
    # Method 1: Generative AI SDK
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt_text)
        if response and response.text:
            return {"speech_response": response.text}
    except Exception as e:
        print(f"SDK Error: {e}")

    # Method 2: Direct REST API (Fallback to avoid SDK/404 model issues)
    if GEMINI_API_KEY:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
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
                return {"speech_response": f"API Error ({res.status_code}): {res_data.get('error', {}).get('message', 'Unknown error')}"}
        except Exception as req_err:
            return {"speech_response": f"Request Error: {str(req_err)}"}

    return {"speech_response": "Error: GEMINI_API_KEY is missing or invalid."}
