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
        # SDK সাপোর্ট অনুযায়ী মডেল সিরিয়ালি চেষ্টা করা
        model_names = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        response_text = None
        
        for name in model_names:
            try:
                model = genai.GenerativeModel(name)
                prompt = f"You are PG AI Assistant. Reply concisely in 1-2 short Bengali sentences to: {req.message}"
                res = model.generate_content(prompt)
                if res and res.text:
                    response_text = res.text
                    break
            except Exception:
                continue

        if response_text:
            return {"speech_response": response_text}
        else:
            return {"speech_response": "কোনো মডেল থেকে উত্তর পাওয়া যায়নি।"}

    except Exception as e:
        print(f"Error detail: {e}")
        return {"speech_response": "দুঃখিত, কোনো একটি সমস্যা হয়েছে।"}
