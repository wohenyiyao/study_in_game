"""闯关链路单测：科目地图 / 科目内链式解锁 / 判分 / 错题本 / 管理端 CRUD 与级联删除。"""
from tests.helpers import register_user, admin_headers


def _answers_for(db, level_id: int) -> list[int]:
    """从库中取某关全部题目的正确答案下标。"""
    from app.models import Question
    qs = db.query(Question).filter(Question.level_id == level_id).order_by(Question.order).all()
    return [q.answer_index for q in qs]


def _wrong_answers_for(db, level_id: int) -> list[int]:
    from app.models import Question
    qs = db.query(Question).filter(Question.level_id == level_id).order_by(Question.order).all()
    return [(q.answer_index + 1) % max(2, len(q.options)) for q in qs]


def _map_levels(client, h):
    """科目地图 → 拍平所有科目的全部关卡。"""
    map_ = client.get("/api/map", headers=h).json()
    return [lv for s in map_ for ch in s["chapters"] for lv in ch["levels"]]


def _seed_python_subject_id(client, h) -> int:
    """取种子科目（python）的 id。"""
    subs = client.get("/api/admin/subjects", headers=h).json()
    return next(s["id"] for s in subs if s["code"] == "python")


def test_unlock_chain_across_chapters(client, db):
    """科目内全局链式解锁：第 2 章第 1 关初始锁定，通关第 1 章第 2 关后解锁。"""
    h = register_user(client, "g1@qq.com")
    levels = _map_levels(client, h)
    assert len(levels) >= 4
    l1, l2, l3 = levels[0], levels[1], levels[2]
    assert l1["unlocked"] and not l1["cleared"]
    assert not l2["unlocked"]
    assert not l3["unlocked"], "同一科目内，第 2 章第 1 关不应提前解锁"

    # 未解锁进入 → 403
    assert client.get(f"/api/levels/{l2['id']}/start", headers=h).status_code == 403

    # 通关 l1
    answers = _answers_for(db, l1["id"])
    r = client.post(f"/api/levels/{l1['id']}/submit", json={"answers": answers}, headers=h)
    j = r.json()
    assert j["passed"] and j["stars"] == 3

    # 通关 l2
    answers = _answers_for(db, l2["id"])
    assert client.post(f"/api/levels/{l2['id']}/submit",
                       json={"answers": answers}, headers=h).json()["passed"]
    # l3 应已解锁
    levels = _map_levels(client, h)
    assert levels[2]["unlocked"]


def test_subjects_independent_chains(client, db):
    """不同科目的第 1 关互不锁定：建一个空关卡的新科目，其关卡可直接挑战。"""
    h = admin_headers(client)
    resp = client.post("/api/admin/subjects",
                       json={"name": "Java 测试", "code": "java", "icon": "☕", "order": 9},
                       headers=h)
    assert resp.status_code == 200, resp.text
    s = resp.json()
    ch = client.post("/api/admin/chapters",
                     json={"subject_id": s["id"], "title": "Java 第 1 章", "order": 0},
                     headers=h).json()
    lv = client.post("/api/admin/levels",
                     json={"chapter_id": ch["id"], "title": "Java L1", "order": 0},
                     headers=h).json()
    q = client.post("/api/admin/questions",
                    json={"level_id": lv["id"], "content": "1+1?", "options": ["2", "3"],
                          "answer_index": 0, "explanation": "x"}, headers=h).json()

    # 普通用户：python 未通关，但 java 科目的关卡应直接解锁可玩
    uh = register_user(client, "g5@qq.com")
    map_ = client.get("/api/map", headers=uh).json()
    java = next(sj for sj in map_ if sj["code"] == "java")
    java_lv = java["chapters"][0]["levels"][0]
    assert java_lv["unlocked"], "新科目首关应默认解锁（科目间互不影响）"
    r = client.post(f"/api/levels/{java_lv['id']}/submit",
                    json={"answers": [0]}, headers=uh)
    assert r.json()["passed"]

    # 清理：删题 → 删关 → 删章 → 删科目
    assert client.delete(f"/api/admin/questions/{q['id']}", headers=h).status_code == 200
    assert client.delete(f"/api/admin/levels/{lv['id']}", headers=h).status_code == 200
    assert client.delete(f"/api/admin/chapters/{ch['id']}", headers=h).status_code == 200
    assert client.delete(f"/api/admin/subjects/{s['id']}", headers=h).status_code == 200


def test_admin_subject_crud_guards(client):
    """科目 CRUD：普通用户禁止；code 唯一；有章节的科目不可删除。"""
    uh = register_user(client, "g6@qq.com")
    assert client.get("/api/admin/subjects", headers=uh).status_code == 403

    h = admin_headers(client)
    s = client.post("/api/admin/subjects",
                    json={"name": "Java", "code": "java", "icon": "☕"}, headers=h)
    assert s.status_code == 200
    sid = s.json()["id"]

    # code 重复被拒
    dup = client.post("/api/admin/subjects",
                      json={"name": "Java 2", "code": "java"}, headers=h)
    assert dup.status_code == 400

    # 更新
    up = client.put(f"/api/admin/subjects/{sid}",
                    json={"name": "Java 面试", "code": "java", "icon": "☕",
                          "description": "d", "order": 1}, headers=h)
    assert up.status_code == 200 and up.json()["name"] == "Java 面试"

    # 有章节 → 不可删
    ch = client.post("/api/admin/chapters",
                     json={"subject_id": sid, "title": "章", "order": 0}, headers=h).json()
    assert client.delete(f"/api/admin/subjects/{sid}", headers=h).status_code == 400
    # 删除章节后可删科目
    assert client.delete(f"/api/admin/chapters/{ch['id']}", headers=h).status_code == 200
    assert client.delete(f"/api/admin/subjects/{sid}", headers=h).status_code == 200


def test_submit_wrong_and_wrongbook(client, db):
    h = register_user(client, "g2@qq.com")
    l1 = _map_levels(client, h)[0]
    answers = _wrong_answers_for(db, l1["id"])
    r = client.post(f"/api/levels/{l1['id']}/submit", json={"answers": answers}, headers=h)
    j = r.json()
    assert not j["passed"] and j["correct"] == 0
    wb = client.get("/api/wrongbook", headers=h).json()
    assert len(wb) == len(answers)
    # 移除一条
    qid = wb[0]["question_id"]
    assert client.delete(f"/api/wrongbook/{qid}", headers=h).status_code == 200
    assert len(client.get("/api/wrongbook", headers=h).json()) == len(answers) - 1


def test_stats(client, db):
    h = register_user(client, "g3@qq.com")
    s = client.get("/api/stats", headers=h).json()
    assert s["total_levels"] >= 4 and s["cleared_levels"] == 0
    l1 = _map_levels(client, h)[0]
    client.post(f"/api/levels/{l1['id']}/submit",
                json={"answers": _answers_for(db, l1["id"])}, headers=h)
    s = client.get("/api/stats", headers=h).json()
    assert s["cleared_levels"] == 1 and s["total_stars"] >= 1


def test_admin_crud_and_delete_with_progress(client, db):
    h = admin_headers(client)
    # 普通用户禁止
    uh = register_user(client, "g4@qq.com")
    assert client.get("/api/admin/users", headers=uh).status_code == 403

    sid = _seed_python_subject_id(client, h)
    # 建 章节→关卡→题目（挂在种子科目下）
    ch = client.post("/api/admin/chapters",
                     json={"subject_id": sid, "title": "测试章", "description": "d",
                           "order": 99}, headers=h)
    assert ch.status_code == 200
    cid = ch.json()["id"]
    assert ch.json()["subject_name"] == "Python 编程"
    lv = client.post("/api/admin/levels",
                     json={"chapter_id": cid, "title": "L", "order": 0}, headers=h)
    lid = lv.json()["id"]
    q = client.post("/api/admin/questions",
                    json={"level_id": lid, "content": "1+1?", "options": ["1", "2", "3"],
                          "answer_index": 1, "explanation": "x"}, headers=h)
    assert q.status_code == 200
    qid = q.json()["id"]

    # 制造该关卡的进度/错题（模拟玩家数据）
    from app.models import Progress, WrongRecord, User
    user = db.query(User).filter(User.email == "g4@qq.com").first()
    db.add(Progress(user_id=user.id, level_id=lid, attempts=1, cleared=1, stars=1,
                    best_accuracy=1.0))
    db.add(WrongRecord(user_id=user.id, question_id=qid, level_id=lid, your_answer=0))
    db.commit()

    # Review 修复点回归：带玩家数据删除关卡/章节不应 FK 报错
    assert client.delete(f"/api/admin/questions/{qid}", headers=h).status_code == 200
    assert client.delete(f"/api/admin/levels/{lid}", headers=h).status_code == 200
    assert client.delete(f"/api/admin/chapters/{cid}", headers=h).status_code == 200
    assert db.query(Progress).filter(Progress.level_id == lid).count() == 0
    assert db.query(WrongRecord).filter(WrongRecord.level_id == lid).count() == 0
