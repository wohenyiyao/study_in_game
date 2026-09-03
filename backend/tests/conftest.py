"""pytest 全局配置。

- 使用独立测试库 learn_quest_test，不污染开发库
- 验证码走 Redis（本机需已启动 redis-server；未启动则相关用例跳过）
- 发邮件被替换为假实现，测试不发真实邮件
"""
import os
import sys
from pathlib import Path

# 必须在 import app 之前设置（database.py 在导入时读环境变量建引擎）
os.environ["LQ_DB_NAME"] = "learn_quest_test"
os.environ["LQ_DB_HOST"] = "127.0.0.1"
os.environ["LQ_DB_PORT"] = "3306"
os.environ["LQ_DB_USER"] = "root"
os.environ["LQ_DB_PASS"] = "root"
os.environ["LQ_DEV_ECHO_CODE"] = "1"   # send-code 回显验证码，便于测试

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # backend/

import pytest  # noqa: E402


@pytest.fixture(scope="session")
def redis_ok():
    from app.redis_client import client
    try:
        ok = bool(client.ping())
    except Exception:
        ok = False
    if not ok:
        pytest.skip("Redis 未启动，跳过依赖 Redis 的用例（启动：E:\\redis\\start_redis.bat）")
    return ok


@pytest.fixture(scope="session")
def db_session_factory(redis_ok):
    """初始化测试库（建库建表 + 种子内容），返回可创建会话的工厂。"""
    from app.database import Base, engine, SessionLocal, ensure_database
    from app.seed import seed
    ensure_database()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed()
    yield SessionLocal


@pytest.fixture()
def db(db_session_factory):
    """每个用例一个干净会话；用例间清空动态数据，保留种子内容。"""
    from app.database import SessionLocal
    from app.models import User, Progress, WrongRecord
    from app.redis_client import client as redis

    session = SessionLocal()
    # 清掉上一用例的动态数据（保留 admin 与种子科目 python）
    session.query(WrongRecord).delete()
    session.query(Progress).delete()
    session.query(User).filter(User.role != "admin").delete()
    # 清理用例中新建的科目（含其章节/关卡/题目，ORM 级联），避免跨用例残留
    from app.models import Subject, Chapter
    extra = session.query(Subject).filter(Subject.code != "python").all()
    for s in extra:
        for ch in list(s.chapters):
            session.delete(ch)
        session.delete(s)
    session.commit()
    session.close()

    # 清掉 Redis 里的验证码/限流 key
    for prefix in ("lq:code:", "lq:rl:"):
        keys = [k for k in redis.scan_iter(f"{prefix}*")]
        if keys:
            redis.delete(*keys)

    yield SessionLocal()


@pytest.fixture()
def client(redis_ok):
    """FastAPI TestClient（每次重建避免状态残留）。"""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.routers import auth_r

    # 发邮件换成假实现，避免真实 SMTP
    auth_r.send_code_email = lambda email, code: None
    with TestClient(app) as c:
        yield c


def register_user(client, email: str, password: str = "test123456") -> dict:
    """send-code(读回显码) → register → 返回 header。"""
    r = client.post("/api/auth/send-code", json={"email": email})
    assert r.status_code == 200, r.text
    code = r.json()["dev_code"]
    r = client.post("/api/auth/register",
                    json={"email": email, "password": password, "code": code})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def admin_headers(client) -> dict:
    r = client.post("/api/auth/login",
                    json={"email": "admin@learn-quest.local", "password": "admin123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}
