"""助教路由：POST /api/assistant/chat —— 对接 agent/tutor.py。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import ChatIn, ChatOut
from ..auth import get_current_user
from ..agent import tutor

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/chat", response_model=ChatOut)
def chat(body: ChatIn, db: Session = Depends(get_db),
         user: User = Depends(get_current_user)):
    reply, ready = tutor.handle_chat(db, user, body.message, body.level_id)
    return ChatOut(reply=reply, agent_ready=ready)
