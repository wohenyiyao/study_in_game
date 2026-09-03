"""数据库引擎与会话（MySQL，轻量服务器/本地均可用）。

连接参数通过环境变量覆盖，默认 127.0.0.1:3306 root/root learn_quest：
    LQ_DB_HOST / LQ_DB_PORT / LQ_DB_USER / LQ_DB_PASS / LQ_DB_NAME
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

_HOST = os.environ.get("LQ_DB_HOST", "127.0.0.1")
_PORT = os.environ.get("LQ_DB_PORT", "3306")
_USER = os.environ.get("LQ_DB_USER", "root")
_PASS = os.environ.get("LQ_DB_PASS", "root")
_NAME = os.environ.get("LQ_DB_NAME", "learn_quest")

DB_URL = (f"mysql+pymysql://{_USER}:{_PASS}@{_HOST}:{_PORT}/{_NAME}"
          "?charset=utf8mb4")

engine = create_engine(DB_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def ensure_database() -> None:
    """连接前确保目标库存在（用 root 连到无库地址建库）。"""
    import pymysql
    conn = pymysql.connect(host=_HOST, port=int(_PORT), user=_USER, password=_PASS)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
    finally:
        conn.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
