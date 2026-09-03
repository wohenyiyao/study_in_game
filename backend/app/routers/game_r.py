"""游戏路由：科目地图 / 关卡题目 / 交卷判分 / 统计 / 错题本。

解锁规则：每个「科目」内部**独立链式解锁**——按 (章节 order, 关卡 order) 排序，
本科目第 1 关恒解锁，第 N 关需第 N-1 关已通关（跨章节延续、跨科目互不影响），
因此 Python / Java / 面试题库等科目各有各的进度线。
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Subject, Chapter, Level, Question, Progress, WrongRecord
from ..schemas import (SubjectMap, ChapterMap, LevelMap, LevelStartOut,
                       QuestionBrief, SubmitIn, SubmitOut, StatsOut, WrongOut, Msg)
from ..auth import get_current_user

router = APIRouter(prefix="/api", tags=["game"])


def _subject_chain(db: Session, subject_id: int) -> list[Level]:
    """某科目内按 章节order→关卡order 排序的全量关卡链。"""
    return (db.query(Level).join(Chapter)
            .filter(Chapter.subject_id == subject_id)
            .order_by(Chapter.order, Level.order)
            .all())


def _subjects_ordered(db: Session) -> list[Subject]:
    return db.query(Subject).order_by(Subject.order, Subject.id).all()


@router.get("/map", response_model=list[SubjectMap])
def get_map(db: Session = Depends(get_db),
            user: User = Depends(get_current_user)):
    """科目地图：每个科目含章节，科目内部链式解锁。"""
    rows = {p.level_id: p for p in db.query(Progress).filter(
        Progress.user_id == user.id, Progress.cleared == 1).all()}
    result = []
    for sub in _subjects_ordered(db):
        chapters = (db.query(Chapter).filter(Chapter.subject_id == sub.id)
                    .order_by(Chapter.order).all())
        ch_items = []
        prev_cleared = True  # 科目内链式：首个关卡恒解锁
        for ch in chapters:
            lv_items = []
            for lv in sorted(ch.levels, key=lambda x: x.order):
                lv_items.append(LevelMap(
                    id=lv.id, title=lv.title, description=lv.description,
                    order=lv.order, pass_ratio=lv.pass_ratio,
                    question_count=len(lv.questions),
                    unlocked=prev_cleared,
                    cleared=lv.id in rows,
                    stars=(rows[lv.id].stars if lv.id in rows else 0),
                    best_accuracy=(rows[lv.id].best_accuracy if lv.id in rows else 0.0)))
                prev_cleared = lv.id in rows
            ch_items.append(ChapterMap(
                id=ch.id, title=ch.title, description=ch.description,
                order=ch.order, levels=lv_items))
        result.append(SubjectMap(
            id=sub.id, name=sub.name, code=sub.code,
            icon=sub.icon or "🎮", description=sub.description,
            order=sub.order, chapters=ch_items))
    return result


@router.get("/levels/{level_id}/start", response_model=LevelStartOut)
def start_level(level_id: int, db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    """开始闯关：返回题目（不含答案）。需已解锁（所在科目链式：上一关已通关）。"""
    level = db.get(Level, level_id)
    if level is None:
        raise HTTPException(404, "关卡不存在")
    chain = _subject_chain(db, level.chapter.subject_id)
    ids = [lv.id for lv in chain]
    if level_id not in ids:
        raise HTTPException(404, "关卡不存在")
    idx = ids.index(level_id)
    if idx > 0:
        prev = chain[idx - 1]
        cleared_prev = (db.query(Progress).filter(
            Progress.user_id == user.id, Progress.level_id == prev.id,
            Progress.cleared == 1).first())
        if cleared_prev is None:
            raise HTTPException(403, "请先通关上一关")
    questions = (db.query(Question).filter(Question.level_id == level_id)
                 .order_by(Question.order).all())
    return LevelStartOut(
        level_id=level.id, title=level.title,
        questions=[QuestionBrief(id=q.id, content=q.content, options=q.options)
                   for q in questions])


def _stars_for(accuracy: float) -> int:
    if accuracy >= 0.9:
        return 3
    if accuracy >= 0.75:
        return 2
    return 1


@router.post("/levels/{level_id}/submit", response_model=SubmitOut)
def submit_level(level_id: int, body: SubmitIn, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    """交卷判分（确定性逻辑，AI 不参与判分）。"""
    questions = (db.query(Question).filter(Question.level_id == level_id)
                 .order_by(Question.order).all())
    level = db.get(Level, level_id)
    if level is None or not questions:
        raise HTTPException(404, "关卡或题目不存在")
    if len(body.answers) != len(questions):
        raise HTTPException(400, "答案数量与题目不一致")

    correct = 0
    details = []
    for q, ans in zip(questions, body.answers):
        ok = (ans == q.answer_index)
        correct += int(ok)
        details.append({
            "question_id": q.id, "your": ans,
            "is_correct": ok, "correct_index": q.answer_index,
            "content": q.content,
            "options": q.options,
            "explanation": q.explanation,
        })
        # 错题本：答错记入，答对清除历史错题
        if not ok:
            db.add(WrongRecord(user_id=user.id, question_id=q.id,
                               level_id=level_id, your_answer=ans))
        else:
            db.query(WrongRecord).filter(
                WrongRecord.user_id == user.id,
                WrongRecord.question_id == q.id).delete()

    total = len(questions)
    accuracy = round(correct / total, 4)
    passed = accuracy >= level.pass_ratio
    stars = _stars_for(accuracy) if passed else 0

    row = (db.query(Progress).filter(
        Progress.user_id == user.id, Progress.level_id == level_id).first())
    if row is None:
        # 显式初始化（Column default 只在 INSERT 时生效）
        row = Progress(user_id=user.id, level_id=level_id,
                       attempts=0, cleared=0, stars=0, best_accuracy=0.0)
        db.add(row)
    row.attempts += 1
    row.cleared = 1 if passed else 0
    if passed:
        row.stars = max(row.stars or 0, stars)
        row.best_accuracy = max(row.best_accuracy or 0, accuracy)
    db.commit()

    return SubmitOut(level_id=level_id, total=total, correct=correct,
                     accuracy=accuracy, passed=passed, stars=stars,
                     details=details)


@router.get("/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db),
              user: User = Depends(get_current_user)):
    """全局统计（跨所有科目合计）。"""
    chain = []
    for sub in _subjects_ordered(db):
        chain.extend(_subject_chain(db, sub.id))
    progress = {p.level_id: p for p in db.query(Progress).filter(
        Progress.user_id == user.id).all()}
    cleared = sum(1 for lv in chain if progress.get(lv.id) and progress[lv.id].cleared)
    stars = sum(p.stars for p in progress.values())
    total_q = sum(len(lv.questions) for lv in chain)
    records = db.query(WrongRecord).filter(WrongRecord.user_id == user.id).count()
    answered = sum(progress[lv.id].attempts * len(lv.questions) for lv in chain
                   if lv.id in progress)
    return StatsOut(total_levels=len(chain), cleared_levels=cleared,
                    total_stars=stars, total_questions=total_q,
                    answered_questions=answered,
                    correct_questions=0, wrong_count=records)


@router.get("/wrongbook", response_model=list[WrongOut])
def wrongbook(db: Session = Depends(get_db),
              user: User = Depends(get_current_user)):
    rows = (db.query(WrongRecord, Question, Level)
            .join(Question, WrongRecord.question_id == Question.id)
            .join(Level, Question.level_id == Level.id)
            .filter(WrongRecord.user_id == user.id)
            .order_by(WrongRecord.created_at.desc()).all())
    out = []
    for rec, q, lv in rows:
        out.append(WrongOut(
            id=rec.id, question_id=q.id, level_id=lv.id, level_title=lv.title,
            content=q.content, options=q.options, answer_index=q.answer_index,
            explanation=q.explanation, your_answer=rec.your_answer,
            created_at=rec.created_at))
    return out


@router.delete("/wrongbook/{question_id}", response_model=Msg)
def remove_wrong(question_id: int, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    db.query(WrongRecord).filter(WrongRecord.user_id == user.id,
                                 WrongRecord.question_id == question_id).delete()
    db.commit()
    return Msg(msg="ok")
