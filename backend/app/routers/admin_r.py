"""管理路由（role=admin）：章节 / 关卡 / 题目 / 用户 CRUD。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Chapter, Level, Question, Progress, WrongRecord
from ..schemas import (ChapterIn, ChapterOut, LevelIn, LevelOut, QuestionIn,
                       QuestionOut, UserOut, Msg)
from ..auth import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"],
                   dependencies=[Depends(require_admin)])


# ---------------- 章节 ----------------
@router.get("/chapters", response_model=list[ChapterOut])
def list_chapters(db: Session = Depends(get_db)):
    out = []
    for ch in db.query(Chapter).order_by(Chapter.order).all():
        item = ChapterOut.model_validate(ch)
        item.level_count = len(ch.levels)
        out.append(item)
    return out


@router.post("/chapters", response_model=ChapterOut)
def create_chapter(body: ChapterIn, db: Session = Depends(get_db)):
    ch = Chapter(**body.model_dump())
    db.add(ch)
    db.commit()
    db.refresh(ch)
    return ChapterOut.model_validate(ch)


@router.put("/chapters/{chapter_id}", response_model=ChapterOut)
def update_chapter(chapter_id: int, body: ChapterIn, db: Session = Depends(get_db)):
    ch = db.get(Chapter, chapter_id)
    if ch is None:
        raise HTTPException(404, "章节不存在")
    for k, v in body.model_dump().items():
        setattr(ch, k, v)
    db.commit()
    db.refresh(ch)
    return ChapterOut.model_validate(ch)


@router.delete("/chapters/{chapter_id}", response_model=Msg)
def delete_chapter(chapter_id: int, db: Session = Depends(get_db)):
    ch = db.get(Chapter, chapter_id)
    if ch is None:
        raise HTTPException(404, "章节不存在")
    level_ids = [lv.id for lv in ch.levels]
    if level_ids:
        # 先清掉引用这些关卡的进度/错题（MySQL 无 ORM 级联）
        db.query(Progress).filter(Progress.level_id.in_(level_ids)).delete(synchronize_session=False)
        db.query(WrongRecord).filter(WrongRecord.level_id.in_(level_ids)).delete(synchronize_session=False)
    db.delete(ch)  # ORM cascade 删除关卡与题目
    db.commit()
    return Msg(msg="ok")


# ---------------- 关卡 ----------------
@router.get("/levels", response_model=list[LevelOut])
def list_levels(chapter_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Level)
    if chapter_id is not None:
        q = q.filter(Level.chapter_id == chapter_id)
    out = []
    for lv in q.order_by(Level.chapter_id, Level.order).all():
        item = LevelOut.model_validate(lv)
        item.question_count = len(lv.questions)
        out.append(item)
    return out


@router.post("/levels", response_model=LevelOut)
def create_level(body: LevelIn, db: Session = Depends(get_db)):
    if db.get(Chapter, body.chapter_id) is None:
        raise HTTPException(404, "章节不存在")
    lv = Level(**body.model_dump())
    db.add(lv)
    db.commit()
    db.refresh(lv)
    return LevelOut.model_validate(lv)


@router.put("/levels/{level_id}", response_model=LevelOut)
def update_level(level_id: int, body: LevelIn, db: Session = Depends(get_db)):
    lv = db.get(Level, level_id)
    if lv is None:
        raise HTTPException(404, "关卡不存在")
    for k, v in body.model_dump().items():
        setattr(lv, k, v)
    db.commit()
    db.refresh(lv)
    return LevelOut.model_validate(lv)


@router.delete("/levels/{level_id}", response_model=Msg)
def delete_level(level_id: int, db: Session = Depends(get_db)):
    lv = db.get(Level, level_id)
    if lv is None:
        raise HTTPException(404, "关卡不存在")
    # 清掉引用该关卡的进度/错题
    db.query(Progress).filter(Progress.level_id == level_id).delete(synchronize_session=False)
    db.query(WrongRecord).filter(WrongRecord.level_id == level_id).delete(synchronize_session=False)
    db.delete(lv)
    db.commit()
    return Msg(msg="ok")


# ---------------- 题目 ----------------
@router.get("/questions", response_model=list[QuestionOut])
def list_questions(level_id: int, db: Session = Depends(get_db)):
    return [QuestionOut.model_validate(q)
            for q in db.query(Question).filter(Question.level_id == level_id)
            .order_by(Question.order).all()]


@router.post("/questions", response_model=QuestionOut)
def create_question(body: QuestionIn, db: Session = Depends(get_db)):
    if db.get(Level, body.level_id) is None:
        raise HTTPException(404, "关卡不存在")
    if not (0 <= body.answer_index < len(body.options)):
        raise HTTPException(400, "答案下标超出选项范围")
    q = Question(**body.model_dump())
    db.add(q)
    db.commit()
    db.refresh(q)
    return QuestionOut.model_validate(q)


@router.put("/questions/{question_id}", response_model=QuestionOut)
def update_question(question_id: int, body: QuestionIn, db: Session = Depends(get_db)):
    q = db.get(Question, question_id)
    if q is None:
        raise HTTPException(404, "题目不存在")
    if not (0 <= body.answer_index < len(body.options)):
        raise HTTPException(400, "答案下标超出选项范围")
    for k, v in body.model_dump().items():
        setattr(q, k, v)
    db.commit()
    db.refresh(q)
    return QuestionOut.model_validate(q)


@router.delete("/questions/{question_id}", response_model=Msg)
def delete_question(question_id: int, db: Session = Depends(get_db)):
    q = db.get(Question, question_id)
    if q is None:
        raise HTTPException(404, "题目不存在")
    # 清掉错题本里的引用
    db.query(WrongRecord).filter(WrongRecord.question_id == question_id).delete(synchronize_session=False)
    db.delete(q)
    db.commit()
    return Msg(msg="ok")


# ---------------- 用户 ----------------
@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return [UserOut.model_validate(u) for u in db.query(User).all()]
