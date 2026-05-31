"""
Tarot Card Interpretation API
FastAPI project that calls Coze bot API to get tarot card meanings
"""

import os
import uuid
import requests
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入数据库模块
from database import init_db, save_reading, get_reading_by_id, get_all_readings, get_readings_by_user, delete_reading

# 初始化数据库
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

# Coze API 配置
COZE_API_KEY = os.getenv("COZE_API_KEY")
COZE_BOT_ID = os.getenv("COZE_BOT_ID")
COZE_API_URL = "https://api.coze.com/v1/chat"

# Webhook 配置
COZE_WEBHOOK_URL = "https://xvxx5bpfs4.coze.site/run"
COZE_WEBHOOK_TOKEN = os.getenv("COZE_WEBHOOK_TOKEN")
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "true").lower() == "true"

def call_coze_webhook(question: str) -> str:
    """调用 Coze Webhook API 获取占卜结果"""
    if not USE_WEBHOOK:
        return f"这是对问题「{question}」的塔罗牌解读。由于未配置Webhook，返回模拟结果。"

    headers = {
        "Content-Type": "application/json"
    }

    if COZE_WEBHOOK_TOKEN:
        headers["Authorization"] = f"Bearer {COZE_WEBHOOK_TOKEN}"

    payload = {
        "question": question
    }

    try:
        response = requests.post(COZE_WEBHOOK_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("interpretation", str(data))
    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Webhook HTTP 错误: {e.response.status_code}, 响应: {e.response.text[:200]}"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Webhook 请求错误: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@app.post("/tarot", response_model=TarotResponse)
async def get_tarot_interpretation(request: TarotRequest):
    """
    获取塔罗牌解读（使用 Coze API）

    请求体: {"card_name": "战车"}
    返回: {"card_name": "战车", "interpretation": "解读内容", "reading_id": "uuid"}
    """
    if not request.card_name or not request.card_name.strip():
        raise HTTPException(status_code=400, detail="card_name 不能为空")

    if not COZE_API_KEY or not COZE_BOT_ID:
        interpretation = f"这是塔罗牌「{request.card_name}」的解读。由于未配置Coze API，返回模拟结果。"
    else:
        interpretation = "Coze API 调用功能需要配置 Bot ID"

    reading_id = str(uuid.uuid4())
    save_reading(reading_id, request.card_name, interpretation)

    return TarotResponse(
        card_name=request.card_name,
        interpretation=interpretation,
        reading_id=reading_id
    )

@app.post("/divination", response_model=DivinationResponse)
async def divination(request: DivinationRequest):
    """
    调用 Coze Webhook 进行占卜

    请求体: {"question": "我的未来运势如何？", "user_id": "optional"}
    返回: {"question": "...", "interpretation": "...", "reading_id": "...", "created_at": "..."}
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="question 不能为空")

    interpretation = call_coze_webhook(request.question.strip())

    reading_id = str(uuid.uuid4())
    save_reading(reading_id, card_name="", interpretation=interpretation, 
                 question=request.question, user_id=request.user_id)

    return DivinationResponse(
        question=request.question,
        interpretation=interpretation,
        reading_id=reading_id,
        created_at=datetime.utcnow()
    )

@app.get("/readings")
async def list_readings(user_id: str = None):
    """
    获取占卜记录列表

    参数: user_id (可选) - 按用户ID筛选
    """
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

@app.get("/readings/{reading_id}")
async def get_reading(reading_id: str):
    """
    根据ID获取单个占卜记录
    """
    reading = get_reading_by_id(reading_id)
    if not reading:
        raise HTTPException(status_code=404, detail="占卜记录不存在")

    return {
        "id": reading.id,
        "card_name": reading.card_name,
        "question": reading.question,
        "interpretation": reading.interpretation,
        "user_id": reading.user_id,
        "created_at": reading.created_at
    }

@app.delete("/readings/{reading_id}")
async def remove_reading(reading_id: str):
    """
    删除占卜记录
    """
    success = delete_reading(reading_id)
    if not success:
        raise HTTPException(status_code=404, detail="占卜记录不存在")

    return {"message": "删除成功"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}

@app.get("/config")
async def get_config():
    """获取当前配置状态"""
    return {
        "COZE_API_KEY_set": bool(COZE_API_KEY),
        "COZE_BOT_ID_set": bool(COZE_BOT_ID),
        "COZE_WEBHOOK_TOKEN_set": bool(COZE_WEBHOOK_TOKEN),
        "USE_WEBHOOK": USE_WEBHOOK
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
