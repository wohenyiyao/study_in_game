"""FastAPI 入口：建表 + 挂载路由 + CORS。"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine, ensure_database
from .routers import auth_r, game_r, admin_r, assistant_r

ensure_database()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Python 闯关学", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 开发用；生产按需收紧
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_r.router)
app.include_router(game_r.router)
app.include_router(admin_r.router)
app.include_router(assistant_r.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
