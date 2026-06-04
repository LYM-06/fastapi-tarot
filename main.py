import os
import uuid
import requests
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from database import init_db, save_reading, get_reading_by_id, get_all_readings, get_readings_by_user, delete_reading

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

COZE_API_KEY = os.getenv("COZE_API_KEY")
COZE_BOT_ID = os.getenv("COZE_BOT_ID")

COZE_WEBHOOK_URL = os.getenv("COZE_WEBHOOK_URL", "https://r4vn2mxn8t.coze.site/stream_run")
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

    payload = {
        "content": {
            "text": question
        }
    }
    try:
        response = requests.post(COZE_WEBHOOK_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.text
        
        # 解析 SSE 格式响应
        lines = data.split('\n')
        final_answer = ''
        for line in lines:
            line = line.strip()
            if line.startswith('data:'):
                try:
                    json_str = line[5:].strip()
                    json_obj = json.loads(json_str)
                    
                    def extract_text(obj):
                        if not obj:
                            return ''
                        if isinstance(obj, str):
                            return obj
                        if 'text' in obj and isinstance(obj['text'], str):
                            return obj['text']
                        if 'content' in obj and isinstance(obj['content'], str):
                            return obj['content']
                        if 'answer' in obj and isinstance(obj['answer'], str):
                            return obj['answer']
                        if 'data' in obj:
                            return extract_text(obj['data'])
                        if 'message' in obj:
                            return extract_text(obj['message'])
                        if 'content' in obj and isinstance(obj['content'], dict):
                            return extract_text(obj['content'])
                        return ''
                    
                    text = extract_text(json_obj)
                    if text:
                        final_answer += text
                except:
                    pass
        
        if not final_answer:
            final_answer = data if len(data) < 500 else data[:500]
        
        return final_answer
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Webhook error: {str(e)}")

async def stream_response(content: str, delay: float = 0.01, chunk_size: int = 4):
    """流式输出内容，按块返回 - 优化后速度更快"""
    for i in range(0, len(content), chunk_size):
        yield content[i:i+chunk_size]
        await asyncio.sleep(delay)

async def stream_coze_response(question: str):
    """直接从 Coze API 流式获取响应并转发"""
    if not USE_WEBHOOK:
        content = f"This is a tarot reading for the question '{question}'. Returning mock result."
        async for chunk in stream_response(content):
            yield chunk
        return
    
    import json
    
    headers = {
        "Content-Type": "application/json"
    }
    if COZE_WEBHOOK_TOKEN:
        headers["Authorization"] = f"Bearer {COZE_WEBHOOK_TOKEN}"
    
    payload = {
        "content": {
            "text": question
        }
    }
    try:
        response = requests.post(
            COZE_WEBHOOK_URL, 
            headers=headers, 
            json=payload, 
            timeout=180,
            stream=True
        )
        response.raise_for_status()
        
        buffer = ""
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:
                buffer += chunk
                
                # 处理 SSE 格式
                while '\n' in buffer:
                    line_end = buffer.index('\n')
                    line = buffer[:line_end].strip()
                    buffer = buffer[line_end+1:]
                    
                    if line.startswith('data:'):
                        try:
                            json_str = line[5:].strip()
                            json_obj = json.loads(json_str)
                            
                            def extract_text(obj):
                                if not obj:
                                    return ''
                                if isinstance(obj, str):
                                    return obj
                                if 'text' in obj and isinstance(obj['text'], str):
                                    return obj['text']
                                if 'content' in obj and isinstance(obj['content'], str):
                                    return obj['content']
                                if 'answer' in obj and isinstance(obj['answer'], str):
                                    return obj['answer']
                                if 'data' in obj:
                                    return extract_text(obj['data'])
                                if 'message' in obj:
                                    return extract_text(obj['message'])
                                if 'content' in obj and isinstance(obj['content'], dict):
                                    return extract_text(obj['content'])
                                return ''
                            
                            text = extract_text(json_obj)
                            if text:
                                # 立即输出获取到的文本
                                for i in range(0, len(text), 4):
                                    yield text[i:i+4]
                                    await asyncio.sleep(0.005)
                        except:
                            pass
        
        # 输出剩余内容
        if buffer:
            yield buffer
            
    except Exception as e:
        yield f"Error: {str(e)}"

@app.post("/tarot", response_model=TarotResponse)
async def get_tarot_interpretation(request: TarotRequest):
    if not request.card_name or not request.card_name.strip():
        raise HTTPException(status_code=400, detail="card_name cannot be empty")

    card_name = request.card_name.strip()
    reading_id = str(uuid.uuid4())

    if not COZE_API_KEY or not COZE_BOT_ID:
        interpretation = f"This is the interpretation for tarot card '{card_name}'. Mock result."
    else:
        interpretation = "Coze API requires Bot ID configuration"

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
    reading_id = str(uuid.uuid4())

    interpretation = call_coze_webhook(question)

    save_reading(reading_id, card_name="", interpretation=interpretation,
                 question=question, user_id=request.user_id)

    return DivinationResponse(
        question=question,
        interpretation=interpretation,
        reading_id=reading_id,
        created_at=datetime.utcnow()
    )

@app.post("/divination/stream")
async def divination_stream(request: DivinationRequest):
    """流式占卜接口 - 立即开始输出结果"""
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")

    question = request.question.strip()
    reading_id = str(uuid.uuid4())
    
    # 使用新的流式响应函数，立即开始返回数据
    async def generate_stream():
        full_response = ""
        async for chunk in stream_coze_response(question):
            full_response += chunk
            yield chunk
        
        # 在流结束后保存到数据库
        save_reading(reading_id, card_name="", interpretation=full_response,
                     question=question, user_id=request.user_id)

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain"
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