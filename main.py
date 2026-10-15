from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS সেটিং (GitHub Pages কে ব্যাকএন্ড কল করার অনুমতি দেওয়া)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # সকল অরিজিন এলাউ করা হচ্ছে
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"status": "Backend running"}

@app.post("/chat")
def chat(req: ChatRequest):
    user_msg = req.message
    # এখানে তোমার AI বা উত্তর দেওয়ার লজিক থাকবে
    bot_reply = f"আমি পেয়েছি: {user_msg}" 
    return {"speech_response": bot_reply}
