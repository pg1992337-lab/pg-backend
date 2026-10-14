import os
import json
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI(title="PG AI Assistant")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
genai.configure(api_key=GEMINI_API_KEY)

pg_system_instruction = """
You are 'PG', an intelligent, 24/7 proactive AI Best Friend, Phone Assistant, and Profit-Focused Financial Advisor.
1. Name: PG. Never refer to yourself as JARVIS.
2. Tone: Speak in natural, casual Bengali (বাংলা) using English loanwords (stock, app, call, profit, target, market).
3. Address: "দোস্ত", "ভাই", or "দাদা".
4. Profit Focus: For stocks, prioritize high momentum and maximum profit generation.
5. Human-in-the-Loop: For stock trade or risky operations, set 'requires_confirmation': true and ask friendly confirmation in speech_response.

JSON Output Schema:
{
    "action_id": "<id>",
    "intent": "STOCK_BUY" | "STOCK_SELL" | "OPEN_APP" | "GET_LOCATION" | "GENERAL_TALK",
    "target": "<symbol/app>",
    "amount_or_quantity": "<amount>",
    "speech_response": "<Bengali voice text>",
    "requires_confirmation": true | false
}
"""

generation_config = {"response_mime_type": "application/json", "temperature": 0.7}
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=pg_system_instruction,
    generation_config=generation_config
)

pending_actions_db = {}

class UserCommandRequest(BaseModel):
    user_speech: str

class UserConfirmationRequest(BaseModel):
    action_id: str
    confirmed: bool

@app.get("/")
def home():
    return {"status": "Online", "assistant": "PG", "message": "কোন খবর দোস্ত?"}

@app.post("/api/v1/process-command")
async def process_command(request: UserCommandRequest):
    try:
        response = model.generate_content(f"User Command: {request.user_speech}")
        data = json.loads(response.text)
        action_id = str(uuid.uuid4())[:8]
        data["action_id"] = action_id
        if data.get("requires_confirmation", False):
            pending_actions_db[action_id] = data
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/confirm-action")
async def confirm_action(request: UserConfirmationRequest):
    action_id = request.action_id
    if action_id not in pending_actions_db:
        raise HTTPException(status_code=404, detail="অ্যাকশন পাওয়া যায়নি!")
    action_item = pending_actions_db.pop(action_id)
    if request.confirmed:
        return {
            "status": "SUCCESS",
            "message": f"কাজ হয়ে গেছে দোস্ত! {action_item.get('intent')} সফল!",
            "speech_response": "তোর কথা মতো কাজ সম্পন্ন করে দিয়েছি ভাই!"
        }
    else:
        return {
            "status": "CANCELLED",
            "message": "ক্যান্সেল করে দেওয়া হয়েছে।",
            "speech_response": "অর্ডার ক্যান্সেল করে দিলাম দোস্ত!"
        }
