import os
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

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY.strip())

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"status": "Backend running"}

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        # gemini-2.5-flash fallback সহ চেষ্টা করা
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = f"You are PG AI Assistant. Reply concisely in 1-2 short Bengali sentences to: {req.message}"
            response = model.generate_content(prompt)
            return {"speech_response": response.text}
        except Exception:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"You are PG AI Assistant. Reply concisely in 1-2 short Bengali sentences to: {req.message}"
            response = model.generate_content(prompt)
            return {"speech_response": response.text}
            
    except Exception as e:
        print(f"Error detail: {e}")
        return {"speech_response": "দুঃখিত, কোনো একটি সমস্যা হয়েছে।"}
