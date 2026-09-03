"""ORM 模型：用户 / 章节 / 关卡 / 题目 / 闯关进度 / 错题记录。"""
from datetime import datetime
from sqlalchemy import (Column, Integer, String, Float, Text, ForeignKey,
                        DateTime, UniqueConstraint, JSON)
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(10), default="user")          # user | admin
    created_at = Column(DateTime, default=datetime.utcnow)


class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, default="")
    order = Column(Integer, default=0)
    levels = relationship("Level", back_populates="chapter",
                          cascade="all, delete-orphan", order_by="Level.order")


class Level(Base):
    __tablename__ = "levels"
    id = Column(Integer, primary_key=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, default="")
    order = Column(Integer, default=0)
    pass_ratio = Column(Float, default=0.6)            # 通关所需正确率
    chapter = relationship("Chapter", back_populates="levels")
    questions = relationship("Question", back_populates="level",
                             cascade="all, delete-orphan", order_by="Question.order")


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False)
    content = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)             # ["选项A", ...]
    answer_index = Column(Integer, nullable=False)     # 正确选项下标
    explanation = Column(Text, default="")             # 标准解析（Agent 可在此基础上个性化讲解）
    order = Column(Integer, default=0)
    level = relationship("Level", back_populates="questions")


class Progress(Base):
    __tablename__ = "progress"
    __table_args__ = (UniqueConstraint("user_id", "level_id", name="uq_user_level"),)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False)
    cleared = Column(Integer, default=0)               # 0未通关 1已通关
    attempts = Column(Integer, default=0)
    best_accuracy = Column(Float, default=0.0)
    stars = Column(Integer, default=0)                 # 0-3
    cleared_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WrongRecord(Base):
    __tablename__ = "wrong_records"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False)
    your_answer = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
