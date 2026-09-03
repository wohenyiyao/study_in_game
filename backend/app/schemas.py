"""Pydantic 请求/响应模型。"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


# ---- 认证 ----
class SendCodeIn(BaseModel):
    email: str


class SendCodeOut(BaseModel):
    msg: str
    dev_code: Optional[str] = None      # 仅 LQ_DEV_ECHO_CODE=1 时返回


class RegisterIn(BaseModel):
    email: str
    password: str
    code: str = ""


class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    role: str
    created_at: Optional[datetime] = None


class LoginOut(BaseModel):
    token: str
    user: UserOut


# ---- 科目（顶层学习单位）----
class SubjectIn(BaseModel):
    name: str
    code: str
    icon: str = "🎮"
    description: str = ""
    order: int = 0


class SubjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    code: str
    icon: str = "🎮"
    description: str = ""
    order: int
    chapter_count: int = 0


# ---- 章节 / 关卡 / 题目（管理端 CRUD）----
class ChapterIn(BaseModel):
    subject_id: int
    title: str
    description: str = ""
    order: int = 0


class ChapterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subject_id: int
    title: str
    description: str
    order: int
    subject_name: str = ""
    level_count: int = 0


class LevelIn(BaseModel):
    chapter_id: int
    title: str
    description: str = ""
    order: int = 0
    pass_ratio: float = 0.6


class LevelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    chapter_id: int
    title: str
    description: str
    order: int
    pass_ratio: float
    question_count: int = 0


class QuestionIn(BaseModel):
    level_id: int
    content: str
    options: List[str]
    answer_index: int
    explanation: str = ""
    order: int = 0


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    level_id: int
    content: str
    options: List[str]
    answer_index: int
    explanation: str
    order: int


# ---- 游戏侧 ----
class LevelMap(BaseModel):
    """地图上一个关卡 + 当前用户的进度视图。"""
    id: int
    title: str
    description: str
    order: int
    pass_ratio: float
    question_count: int
    unlocked: bool
    cleared: bool
    stars: int
    best_accuracy: float


class ChapterMap(BaseModel):
    id: int
    title: str
    description: str
    order: int
    levels: List[LevelMap]


class SubjectMap(BaseModel):
    """地图顶层：一个科目（如 Python），含其章节与（科目内独立的）关卡链。"""
    id: int
    name: str
    code: str
    icon: str = "🎮"
    description: str = ""
    order: int
    chapters: List[ChapterMap]


class QuestionBrief(BaseModel):
    id: int
    content: str
    options: List[str]


class LevelStartOut(BaseModel):
    level_id: int
    title: str
    questions: List[QuestionBrief]


class SubmitIn(BaseModel):
    answers: List[int]        # 与题目顺序一一对应


class SubmitOut(BaseModel):
    level_id: int
    total: int
    correct: int
    accuracy: float
    passed: bool
    stars: int
    details: List[dict]       # 每题：question_id/your/is_correct/explanation


class StatsOut(BaseModel):
    total_levels: int
    cleared_levels: int
    total_stars: int
    total_questions: int
    answered_questions: int
    correct_questions: int
    wrong_count: int


class WrongOut(BaseModel):
    id: int
    question_id: int
    level_id: int
    level_title: str
    content: str
    options: List[str]
    answer_index: int
    explanation: str
    your_answer: int
    created_at: Optional[datetime] = None


class Msg(BaseModel):
    msg: str


# ---- 助教（Agent 接口）----
class ChatIn(BaseModel):
    message: str
    level_id: Optional[int] = None


class ChatOut(BaseModel):
    reply: str
    agent_ready: bool
