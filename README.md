# Python 闯关学（learn-quest）

游戏式 Python 学习闯关网站：注册（QQ 邮箱验证码）→ 学习地图 → 按关卡顺序答题闯关（≥60% 通关、按正确率得 1-3 星）→ 错题自动入错题本；管理员可在线维护章节/关卡/题目。内置「AI 助教」Agent 开发位（当前为占位回复，由你接入 LangGraph）。

## 技术栈

- 后端：Python FastAPI + SQLAlchemy + MySQL + Redis（验证码）+ JWT(HMAC，标准库)
- 前端：Vue 3 + Vite + Element Plus + Pinia + Vue Router
- 部署目标：轻量云服务器（本项目不含重组件，单机即可）

## 目录

```
learn-quest/
├── backend/            FastAPI 后端
│   ├── app/
│   │   ├── main.py         入口（建库建表 + 路由 + CORS）
│   │   ├── models.py       ORM（用户/章节/关卡/题目/进度/错题）
│   │   ├── schemas.py      Pydantic 模型
│   │   ├── auth.py         PBKDF2 密码 + HMAC 令牌
│   │   ├── emailer.py      QQ 邮箱 SMTP 发验证码
│   │   ├── redis_client.py 验证码 Redis 存储
│   │   ├── routers/        auth / game / admin / assistant
│   │   ├── agent/          🤖 Agent 开发位（tutor.py，等你实现）
│   │   └── seed.py         种子数据（管理员 + 2章4关20题）
│   ├── tests/             pytest 单测（12 条，全绿）
│   └── run.py
├── frontend/           Vue3 前端（登录/地图/答题/错题本/战绩/管理后台）
└── AGENT_TODO.md       你的 Agent 练习任务书
```

## 本地启动

**前置**：MySQL（库自动创建，连接见 `backend/.env.example`）、Redis（`E:\redis\start_redis.bat`）、Python 3.12、Node 20。
验证码邮件：仓库**不内置 SMTP 凭据**——本地联调设环境变量 `LQ_DEV_ECHO_CODE=1`
（send-code 直接回显验证码、不真发信），或复制 `backend/.env.example` 为 `.env`
填入自己的 QQ 邮箱 + SMTP 授权码。

```bash
# 后端
cd backend
pip install -r requirements.txt
python -m app.seed          # 首次：管理员 + 题库
python run.py               # http://127.0.0.1:8000

# 前端（另开终端）
cd frontend
npm install
npm run dev                 # http://127.0.0.1:5173 （已配 /api 代理到 8000）
```

默认账号：管理员 `admin@learn-quest.local / admin123`（**上线前必须改**）。

## 测试

```bash
cd backend
python -m pytest tests -v    # 需 Redis 已启动；使用独立库 learn_quest_test
```

## Agent 开发位

见 [AGENT_TODO.md](AGENT_TODO.md)：把 `backend/app/agent/tutor.py` 的占位实现替换成
LangGraph Agent（可复用你 langgraph-study 的客服多 Agent 技能）。

## 生产部署提示

见 [backend/.env.example](backend/.env.example) —— 务必设置固定 `LQ_SECRET`
（未设置则每次启动随机生成、重启后登录态全失效）、配置 `LQ_MAIL_USER` 与 `LQ_MAIL_CODE`
（SMTP 授权码，代码不再内置默认邮箱）、关闭 `LQ_DEV_ECHO_CODE`、把数据库密码移入环境变量、收紧 CORS。
