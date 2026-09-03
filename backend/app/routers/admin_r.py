"""管理路由（role=admin）：科目 / 章节 / 关卡 / 题目 / 用户 CRUD。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Subject, Chapter, Level, Question, Progress, WrongRecord
from ..schemas import (SubjectIn, SubjectOut, ChapterIn, ChapterOut,
                       LevelIn, LevelOut, QuestionIn, QuestionOut, UserOut, Msg)
from ..auth import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"],
                   dependencies=[Depends(require_admin)])


# ---------------- 科目 ----------------
@router.get("/subjects", response_model=list[SubjectOut])
def list_subjects(db: Session = Depends(get_db)):
    out = []
    for s in db.query(Subject).order_by(Subject.order, Subject.id).all():
        item = SubjectOut.model_validate(s)
        item.chapter_count = len(s.chapters)
        out.append(item)
    return out


@router.post("/subjects", response_model=SubjectOut)
def create_subject(body: SubjectIn, db: Session = Depends(get_db)):
    if db.query(Subject).filter(Subject.code == body.code).first():
        raise HTTPException(400, "科目编码已存在（code 需唯一，如 python / java）")
    s = Subject(**body.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return SubjectOut.model_validate(s)


@router.put("/subjects/{subject_id}", response_model=SubjectOut)
def update_subject(subject_id: int, body: SubjectIn, db: Session = Depends(get_db)):
    s = db.get(Subject, subject_id)
    if s is None:
        raise HTTPException(404, "科目不存在")
    dup = db.query(Subject).filter(Subject.code == body.code,
                                   Subject.id != subject_id).first()
    if dup:
        raise HTTPException(400, "科目编码已存在（code 需唯一，如 python / java）")
    for k, v in body.model_dump().items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return SubjectOut.model_validate(s)


@router.delete("/subjects/{subject_id}", response_model=Msg)
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    s = db.get(Subject, subject_id)
    if s is None:
        raise HTTPException(404, "科目不存在")
    if s.chapters:
        raise HTTPException(400, "该科目下还有章节，请先删除其下的全部章节")
    db.delete(s)
    db.commit()
    return Msg(msg="ok")


# ---------------- 章节 ----------------
@router.get("/chapters", response_model=list[ChapterOut])
def list_chapters(subject_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Chapter)
    if subject_id is not None:
        q = q.filter(Chapter.subject_id == subject_id)
    out = []
    for ch in q.order_by(Chapter.subject_id, Chapter.order).all():
        item = ChapterOut.model_validate(ch)
        item.subject_name = ch.subject.name if ch.subject else ""
        item.level_count = len(ch.levels)
        out.append(item)
    return out


@router.post("/chapters", response_model=ChapterOut)
def create_chapter(body: ChapterIn, db: Session = Depends(get_db)):
    if db.get(Subject, body.subject_id) is None:
        raise HTTPException(404, "科目不存在")
    ch = Chapter(**body.model_dump())
    db.add(ch)
    db.commit()
    db.refresh(ch)
    item = ChapterOut.model_validate(ch)
    item.subject_name = ch.subject.name if ch.subject else ""
    return item


@router.put("/chapters/{chapter_id}", response_model=ChapterOut)
def update_chapter(chapter_id: int, body: ChapterIn, db: Session = Depends(get_db)):
    ch = db.get(Chapter, chapter_id)
    if ch is None:
        raise HTTPException(404, "章节不存在")
    if db.get(Subject, body.subject_id) is None:
        raise HTTPException(404, "科目不存在")
    for k, v in body.model_dump().items():
        setattr(ch, k, v)
    db.commit()
    db.refresh(ch)
    item = ChapterOut.model_validate(ch)
    item.subject_name = ch.subject.name if ch.subject else ""
    return item


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
