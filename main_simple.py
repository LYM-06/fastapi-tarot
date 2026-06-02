"""
Simplified Tarot API (without Redis cache)
"""

import os
import uuid
import requests
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database module
from database import init_db, save_reading, get_reading_by_id, get_all_readings, get_readings_by_user, delete_reading

# Initialize database
init_db()

app = FastAPI(title="Tarot Card API")

class TarotRequest(BaseModel):
    card_name: str

class TarotResponse(BaseModel):
    card_name: str
    interpretation: str
    reading_id: str

class DivinationRequest(BaseModel):
    question: str
    user_id: str = None

class DivinationResponse(BaseModel):
    question: str
    interpretation: str
    reading_id: str
    created_at: datetime

# Coze API Configuration
COZE_API_KEY = os.getenv("COZE_API_KEY")
COZE_BOT_ID = os.getenv("COZE_BOT_ID")

# Webhook Configuration
COZE_WEBHOOK_URL = "https://xvxx5bpfs4.coze.site/run"
COZE_WEBHOOK_TOKEN = os.getenv("COZE_WEBHOOK_TOKEN")
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "true").lower() == "true"

def call_coze_webhook(question: str) -> str:
    if not USE_WEBHOOK:
        return f"This is a tarot reading for the question '{question}'. Returning mock result."

    headers = {
        "Content-Type": "application/json"
    }
    if COZE_WEBHOOK_TOKEN:
        headers["Authorization"] = f"Bearer {COZE_WEBHOOK_TOKEN}"

    payload = {"question": question}
    try:
        response = requests.post(COZE_WEBHOOK_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("interpretation", str(data))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Webhook error: {str(e)}")

@app.post("/tarot", response_model=TarotResponse)
async def get_tarot_interpretation(request: TarotRequest):
    if not request.card_name or not request.card_name.strip():
        raise HTTPException(status_code=400, detail="card_name cannot be empty")

    card_name = request.card_name.strip()
    if not COZE_API_KEY or not COZE_BOT_ID:
        interpretation = f"This is the interpretation for tarot card '{card_name}'. Mock result."
    else:
        interpretation = "Coze API requires Bot ID configuration"

    reading_id = str(uuid.uuid4())
    save_reading(reading_id, card_name, interpretation)

    return TarotResponse(
        card_name=card_name,
        interpretation=interpretation,
        reading_id=reading_id
    )

@app.post("/divination", response_model=DivinationResponse)
async def divination(request: DivinationRequest):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")

    question = request.question.strip()
    interpretation = call_coze_webhook(question)

    reading_id = str(uuid.uuid4())
    save_reading(reading_id, card_name="", interpretation=interpretation, 
                 question=question, user_id=request.user_id)

    return DivinationResponse(
        question=question,
        interpretation=interpretation,
        reading_id=reading_id,
        created_at=datetime.utcnow()
    )

@app.get("/readings")
async def list_readings(user_id: str = None):
    if user_id:
        readings = get_readings_by_user(user_id)
    else:
        readings = get_all_readings()

    return [{
        "id": r.id,
        "card_name": r.card_name,
        "question": r.question,
        "interpretation": r.interpretation,
        "user_id": r.user_id,
        "created_at": r.created_at
    } for r in readings]

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
