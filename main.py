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
    # যেসব মডেল কাজ করতে পারে তাদের ফুল পাথ
    candidates = [
        "models/gemini-1.5-flash",
        "models/gemini-1.5-flash-latest",
        "models/gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]
    
    last_error = ""
    
    for model_name in candidates:
        try:
            model = genai.GenerativeModel(model_name)
            prompt = f"You are PG AI Assistant. Reply concisely in 1-2 short Bengali sentences to: {req.message}"
            response = model.generate_content(prompt)
            if response and response.text:
                return {"speech_response": response.text}
        except Exception as e:
            last_error = str(e)
            continue
            
    return {"speech_response": f"Error: {last_error}"}
