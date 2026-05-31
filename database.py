"""
Database module for Tarot readings
Stores user divination requests and results
"""

import asyncio
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库配置
DATABASE_URL = "sqlite:///./tarot.db"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


class TarotReading(Base):
    """塔罗牌占卜记录模型"""
    __tablename__ = "tarot_readings"

    id = Column(String, primary_key=True, index=True)
    card_name = Column(String, index=True)
    question = Column(Text, nullable=True)
    interpretation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, nullable=True, index=True)


# 创建数据库表
def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_reading(reading_id: str, card_name: str, interpretation: str, 
                 question: str = None, user_id: str = None):
    """保存占卜记录"""
    db = SessionLocal()
    try:
        reading = TarotReading(
            id=reading_id,
            card_name=card_name,
            question=question,
            interpretation=interpretation,
            user_id=user_id
        )
        db.add(reading)
        db.commit()
        db.refresh(reading)
        return reading
    finally:
        db.close()


def get_reading_by_id(reading_id: str) -> Optional[TarotReading]:
    """根据ID获取占卜记录"""
    db = SessionLocal()
    try:
        return db.query(TarotReading).filter(TarotReading.id == reading_id).first()
    finally:
        db.close()


def get_all_readings() -> List[TarotReading]:
    """获取所有占卜记录"""
    db = SessionLocal()
    try:
        return db.query(TarotReading).order_by(TarotReading.created_at.desc()).all()
    finally:
        db.close()


def get_readings_by_user(user_id: str) -> List[TarotReading]:
    """根据用户ID获取占卜记录"""
    db = SessionLocal()
    try:
        return db.query(TarotReading).filter(TarotReading.user_id == user_id)\
            .order_by(TarotReading.created_at.desc()).all()
    finally:
        db.close()


def delete_reading(reading_id: str) -> bool:
    """删除占卜记录"""
    db = SessionLocal()
    try:
        reading = db.query(TarotReading).filter(TarotReading.id == reading_id).first()
        if reading:
            db.delete(reading)
            db.commit()
            return True
        return False
    finally:
        db.close()
