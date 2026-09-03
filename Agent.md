# Agent.md —— learn-quest（Python 闯关学）

> 本文档给 Agent / 开发者快速理解本仓库：**项目是什么、目录结构、数据模型、API、
> 认证、配置、如何跑起来与跑测试、代码约定，以及留给 Agent 的「AI 助教」开发位**。
> 所有注释、UI 文案、API 错误 `detail` 均为**中文**，请遵循。

---

## 1. 项目概述

游戏式**编程学习闯关网站**（**多科目**：当前内置 Python，可扩展 Java / 面试题库等科目），完整业务闭环：

1. 用户用 **QQ 邮箱 + 邮件验证码注册**，邮箱 + 密码登录（JWT 令牌）。
2. 进入「学习地图」（按**科目**切换），科目内按 **章节 → 关卡 → 题目** 顺序闯关（**科目内链式解锁**：本科目通上一关才能开下一关、跨章节延续；**科目之间互不影响**，各有独立进度线）。
3. 交卷后端**确定性判分**（AI 不参与判分）：正确率 ≥ 关卡 `pass_ratio`（默认 0.6）即通关，按正确率得 **1–3 星**（≥90% → 3 星，≥75% → 2 星，其余通关 1 星）。
4. 答错的题**自动进错题本**；答对则该题从错题本清除。
5. 管理员可在后台在线维护 **科目 / 章节 / 关卡 / 题目 / 用户**（CRUD，含级联删除与玩家数据清理）。
6. 「我的战绩」页展示统计。
7. 答题页右下角 🤖 **AI 助教**抽屉 → `POST /api/assistant/chat` → 目前后端是**占位实现**（`agent_ready=False`），这是留给 Agent 用 LangGraph 接成真 Agent 的**开发位**（见 §10 与根目录 `AGENT_TODO.md`）。

仓库已接入 git 并推送至 GitHub：https://github.com/wohenyiyao/study_in_game（分支 main）。
本地已装好 `backend/.venv`（Python 3.12.10）与 `frontend/node_modules`。

## 2. 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.12 + FastAPI + SQLAlchemy 2.0 + **MySQL**（pymysql）+ Redis（验证码）+ Pydantic v2 |
| 认证 | 纯标准库自研：PBKDF2 密码哈希 + HMAC-SHA256 签名 JWT 风格令牌（无第三方依赖） |
| 邮件 | `smtplib` SMTP_SSL 发 QQ 邮箱验证码（零依赖） |
| 前端 | Vue 3（`<script setup>`）+ Vite 6 + Element Plus（zh-cn）+ Pinia + Vue Router + axios |
| 测试 | pytest + FastAPI TestClient（用独立库 `learn_quest_test`，需 MySQL + Redis） |

前端 API 走 Vite 代理：`/api → http://127.0.0.1:8000`。

## 3. 目录结构

```
learn-quest/
├── Agent.md                     ← 本文档（给 Agent 的仓库导览）
├── README.md                    ← 面向人的启动说明
├── AGENT_TODO.md                ← ★ AI 助教 Agent 任务书（开发位需求/验收清单）
├── backend/                     FastAPI 后端
│   ├── run.py                   开发入口：uvicorn app.main:app --reload (127.0.0.1:8000)
│   ├── requirements.txt         仅 7 个依赖（见 §2）；无 langgraph（Agent 接入时需新增）
│   ├── .env.example             环境变量样例（MySQL/Redis/SECRET/SMTP/开发回显开关）
│   ├── learn_quest.db           57KB SQLite 残留文件——代码里无任何引用，纯历史遗留，可忽略/删除
│   ├── app/
│   │   ├── main.py              FastAPI 入口：ensure_database + create_all + CORS(*, 开发用) + 挂 4 个 router + /api/health
│   │   ├── database.py          ★ MySQL 引擎与会话（env: LQ_DB_*），ensure_database() 自动建库；get_db() 依赖
│   │   ├── models.py            ★ ORM 模型：Subject/User/Chapter/Level/Question/Progress/WrongRecord（见 §4）
│   │   ├── schemas.py           ★ Pydantic v2 请求/响应模型（from_attributes=True），前后端接口契约的"真源"
│   │   ├── auth.py              ★ PBKDF2 哈希 + HMAC JWT（env: LQ_SECRET，7 天过期）；get_current_user / require_admin 依赖
│   │   ├── emailer.py           QQ 邮箱 SMTP_SSL 发验证码（env: LQ_MAIL_*）
│   │   ├── redis_client.py      Redis 客户端（env: LQ_REDIS_URL），默认 127.0.0.1:6379/0
│   │   ├── seed.py              种子数据：科目 python（管理员 + 2 章 4 关 20 题）；python -m app.seed 可跑
│   │   ├── routers/
│   │   │   ├── auth_r.py        /api/auth/*：send-code / register / login / me（验证码存 Redis，60s 限流）
│   │   │   ├── game_r.py        /api/map（科目地图）、/api/levels/{id}/start|submit、/api/stats、/api/wrongbook（判分逻辑全在这里）
│   │   │   ├── admin_r.py       /api/admin/*：科目/章节/关卡/题目/用户 CRUD（router 级 require_admin）
│   │   │   └── assistant_r.py   /api/assistant/chat → 转发给 agent/tutor.py
│   │   └── agent/
│   │       └── tutor.py         ★ AI 助教开发位（当前占位，collect_context 已有雏形）
│   ├── tests/
│   │   ├── conftest.py          env 注入（learn_quest_test 库 + 验证码回显）、fixtures、helpers
│   │   ├── helpers.py           register_user / admin_headers
│   │   ├── test_auth.py         6 条：注册链路/错误码/一次性码/重复邮箱/登录/限流
│   │   ├── test_game_admin.py   6 条：科目地图/科目独立链式解锁/判分错题本/统计/管理 CRUD 与级联删除
│   │   └── test_agent.py        2 条：占位助教断言 + 未登录 401（Agent 落地后需改成真实断言）
│   └── .venv/                   ★ 本地虚拟环境（Python 3.12.10），运行/测试请用它
└── frontend/                    Vue3 前端
    ├── package.json / vite.config.js   dev/build；/api 代理到 8000
    ├── index.html
    └── src/
        ├── main.js              注册 ElementPlus(zh-cn) + 全部图标 + Pinia + Router
        ├── App.vue
        ├── api/http.js          ★ axios 单例：baseURL /api；请求加 Bearer；响应剥 data；401 清登录跳 /login；错误 ElMessage
        ├── stores/user.js       ★ Pinia：token/user 持久化(localStorage: lq_token/lq_user)；isLogin/isAdmin
        ├── router/index.js      路由 + 守卫（未登录 → /login；admin 页需 isAdmin）
        └── views/
            ├── LoginView.vue    登录/注册（含发验证码按钮）
            ├── Layout.vue       侧边导航（地图/战绩/错题本 + admin 内容管理）
            ├── MapView.vue      科目学习地图（GET /map 按科目返回）
            ├── QuizView.vue     ★ 答题 + 交卷结果讲解 + 🤖 AI 助教抽屉（POST /assistant/chat，附 level_id）
            ├── WrongbookView.vue  错题本（列表/删除）
            ├── StatsView.vue    我的战绩
            └── admin/           AdminSubjects / AdminChapters / AdminLevels / AdminQuestions / AdminUsers
```

## 4. 数据模型（`backend/app/models.py`）

| 表 | 关键字段 | 说明 |
|---|---|---|
| `subjects` | **name**(唯一), **code**(唯一，如 python/java), icon(emoji), description, order | 顶层科目；每个科目有**独立**的链式解锁进度 |
| `users` | email(唯一), password_hash, role(`user`\|`admin`) | 密码为 PBKDF2 哈希 |
| `chapters` | **subject_id**(FK→subjects), title, description, order | 章节挂在科目下 |
| `levels` | chapter_id, title, description, order, **pass_ratio**(默认 0.6) | 每章多个关卡；ORM 级联删除题目 |
| `questions` | level_id, content, **options(JSON 数组)**, **answer_index**, explanation, order | 单选；explanation 是标准解析（Agent 讲解的素材） |
| `progress` | (user_id, level_id) 唯一, cleared, attempts, best_accuracy, **stars**, cleared_at, updated_at | 每人每关一条进度；保留历史最佳 |
| `wrong_records` | user_id, question_id, level_id, your_answer, created_at | 错题本 |

**判分/星级规则（game_r.py）**：`correct/total` ≥ `pass_ratio` 通关；星级 `≥0.9→3`、`≥0.75→2`、否则通关 `1`。答错写 `wrong_records`，答对删除同题历史错题。`progress.stars/best_accuracy` 只保留历史最大值，`cleared` 反映最近一次交卷。

**解锁规则（关键业务逻辑）**：**按科目**取 (章节 order, 关卡 order) 排序后**科目内链式解锁**——
每个科目的第 1 关恒解锁，第 N 关需本科目第 N-1 关 `cleared=1`（跨章节延续、**跨科目互不影响**）。
同一逻辑在 `/map` 与 `/levels/{id}/start`(403) 中各有一份实现，改动需同步
（测试 `test_unlock_chain_across_chapters`、`test_subjects_independent_chains` 覆盖回归）。

**管理端删除的注意事项（admin_r.py）**：MySQL 无 ORM 级联，删除题目/关卡/章节前**手动清掉引用它们的 progress / wrong_records**（测试已回归）；**科目**若仍有章节则后端拒绝删除（须先删净其下章节）。

## 5. API 一览（统一前缀 /api，除登录外均需 `Authorization: Bearer <token>`）

| 方法与路径 | 功能 |
|---|---|
| `GET /health` | 健康检查 |
| `POST /auth/send-code` | 发邮箱验证码；503 Redis 不可用、400 格式/已注册、429 60s 限流；`LQ_DEV_ECHO_CODE=1` 时响应带 `dev_code` |
| `POST /auth/register` | `{email,password,code}` → `{token,user}`（验证码一次性） |
| `POST /auth/login` | `{email,password}` → `{token,user}` |
| `GET /auth/me` | 当前用户 |
| `GET /map` | 科目地图（每个科目含章节树；关卡含 unlocked/cleared/stars/best_accuracy，科目内链式解锁） |
| `GET /levels/{id}/start` | 返回题目（**不含答案**，只含 id/content/options）；未解锁 403 |
| `POST /levels/{id}/submit` | `{answers:[int]}` → 判分结果 + 每题 details（含解析），维护进度与错题本 |
| `GET /stats` | 关卡数/通关数/星数/题目数/错题数 |
| `GET /wrongbook` | 错题列表（含答案与解析）；`DELETE /wrongbook/{question_id}` 移除 |
| `GET|POST|PUT|DELETE /admin/subjects[/{id}]` | 科目 CRUD（GET 带 chapter_count；code 唯一；有章节的科目拒删） |
| `GET|POST|PUT|DELETE /admin/chapters[/{id}]` | 章节 CRUD（GET 支持 `?subject_id=`；需带 subject_id） |
| `GET|POST|PUT|DELETE /admin/levels[/{id}]` | 关卡 CRUD（GET 支持 `?chapter_id=`） |
| `GET|POST|PUT|DELETE /admin/questions[/{id}]` | 题目 CRUD（GET 需 `?level_id=`） |
| `GET /admin/users` | 用户列表 |
| `POST /assistant/chat` | ★ AI 助教：`{message, level_id?}` → `{reply, agent_ready}`（见 §10） |

## 6. 认证与安全约定（`auth.py`）

- 密码：`hashlib.pbkdf2_hmac("sha256", 100_000 轮, 16B 盐)`，存为 `urlsafe_base64(salt).urlsafe_base64(dk)`。
- 令牌：自研 HMAC-SHA256 JWT 风格 `header.payload.signature`，payload 含 `uid/role/exp`，**默认 7 天过期**；密钥取环境变量 `LQ_SECRET`（未设置则每次启动随机生成）。
- 依赖：`get_current_user`（解析 Bearer + 查库）、`require_admin`（叠加 role 检查，admin router 级使用）。
- ⚠️ **凭据策略（代码已清洗，勿回退）**：`emailer.py` 不再内置任何默认邮箱/授权码，
  只从 `LQ_MAIL_USER / LQ_MAIL_CODE` 环境变量读取（未配置时发信直接抛错）；
  `auth.py` 的 `LQ_SECRET` 未设置时每次启动随机生成（重启后旧令牌失效）。
  写代码/文档时同样**不要把真实凭据硬编码进仓库**（测试发信已被 conftest 替换为假实现）。

## 7. 配置（环境变量，见 `backend/.env.example`）

| 变量 | 默认 | 用途 |
|---|---|---|
| `LQ_DB_HOST/PORT/USER/PASS/NAME` | 127.0.0.1:3306 root/root learn_quest | MySQL；`ensure_database()` 启动时自动建库 |
| `LQ_REDIS_URL` | redis://127.0.0.1:6379/0 | 验证码/限流存储（Redis key：`lq:code:<email>` 存验证码 sha256、TTL 600s；`lq:rl:<email>` INCR 限流 60s） |
| `LQ_SECRET` | 无（未设置则每次启动随机生成） | 令牌签名密钥；生产/多进程必须固定 |
| `LQ_MAIL_HOST/PORT/USER/CODE/FROM` | smtp.qq.com:465；USER/CODE 无默认 | 邮件 SMTP；`CODE` 是授权码；未配置 USER/CODE 时发信抛错 |
| `LQ_DEV_ECHO_CODE` | 0 | `=1` 时 send-code **跳过真实 SMTP**、直接回显验证码（本地联调用，生产关闭） |

## 8. 本地启动与测试

```bash
# 前置：MySQL(库自动创建) + Redis(如 E:\redis\start_redis.bat)
# 后端（建议用仓库内 .venv）
cd backend
.\.venv\Scripts\python -m app.seed   # 首次：管理员 + 种子题库（2 章 4 关 20 题）
.\.venv\Scripts\python run.py        # http://127.0.0.1:8000 （--reload）

# 前端（另开终端）
cd frontend
npm run dev                          # http://127.0.0.1:5173 （/api 代理到 8000）
```

默认账号：管理员 `admin@learn-quest.local / admin123`（上线前必须改）。

```bash
# 测试：需 MySQL + Redis 在跑；使用独立库 learn_quest_test（不污染开发数据）
cd backend
.\.venv\Scripts\python -m pytest tests -v    # 14 条；Redis 未启动则整组跳过
```

测试基础设施要点（`tests/conftest.py`）：在 import app **之前**设好 `LQ_DB_NAME=learn_quest_test`、`LQ_DEV_ECHO_CODE=1`；session 级建表 + seed；每条用例清动态数据、保留种子内容；发信替换为 lambda 假实现。新增用例请沿用 fixtures 与 helpers，不要发真实邮件、不要动开发库。

## 9. 代码约定（请遵守，利于协作与测试）

1. **语言**：注释/docstring/UI 文案/错误 `detail` 一律中文；命名仍用英文。
2. **接口契约优先**：`schemas.py` 是请求/响应模型的真源；改 API **必须同步改 schemas 与前端调用方**——尤其 `AGENT_TODO.md` 定死的 `ChatIn/ChatOut`（`{reply, agent_ready}`）**不要动**。
3. 判分、解锁、星级是**确定性后端逻辑**，不要把 AI 混入判分链路。
4. 路由文件按域拆分（auth/game/admin/assistant），依赖注入 `Depends(get_db)` / `Depends(get_current_user|require_admin)`。
5. 涉及删除的接口要**手动清理** progress/wrong_records 外键引用（MySQL 无级联）。
6. 生产安全项：CORS 收紧、`LQ_SECRET`/SMTP/DB 密码进环境变量、关闭 `LQ_DEV_ECHO_CODE`。
7. 新依赖要同步 `requirements.txt`；改动要补/改 `backend/tests/` 里的回归用例。

## 10. ★ AI 助教 Agent 开发位（当前唯一"未完成"的功能）

- **现状**：`backend/app/agent/tutor.py` 的 `handle_chat(db, user, message, level_id)` 只返回占位文本、`agent_ready=False`；`test_agent.py` 因此断言占位行为。
- **前端已就绪**：答题页 `QuizView.vue` 右下角 🤖 抽屉 → `POST /api/assistant/chat {message, level_id}` → 展示 `reply`；你**只改后端**（tutor.py，可加文件），不要改前端与接口契约。
- **任务书**：**根目录 `AGENT_TODO.md`** —— 分阶段把占位换成 LangGraph Agent：阶段 A 做 `@tool` 工具（查进度/取关卡题/知识检索/给渐进提示）、阶段 B 用 MemorySaver + `thread_id=user.id` 做记忆、阶段 C（可选）多 Agent 分流。验收：答错不直接给答案、能讲清"为什么选 tuple"、追问有记忆、`agent_ready=True`，并把真实对话场景补进 `test_agent.py`。
- **已有素材**：`tutor.collect_context()` 已能取「通关数/当前关卡」，可升级为工具；`Question.explanation`、`WrongRecord`、`Progress` 都是 Agent 可用的实时上下文。LLM 可走本机 DeepSeek API 或 Ollama qwen2.5:3b（key 等见任务书，不外泄到仓库文档）。
- 提示：`handle_chat` 是无状态 HTTP 调用，做记忆时考虑**模块级 compiled agent + invoke 传 `{"configurable": {"thread_id": uid}}`**；接入后把 `agent_ready` 置 True。

## 11. 常见坑速查

- `learn_quest.db`（backend 根）是 **SQLite 残留文件，代码无任何引用**，别用它判断库结构，也别把它当目标库。
- 真正的库是 **MySQL**（`learn_quest_test` 是测试库）；Redis 挂了 → send-code 503、pytest 整组跳过。
- 升级过「科目」结构后，旧开发库 `learn_quest` 缺 `subjects` 表：先 `DROP DATABASE learn_quest` 再 `python -m app.seed` 重建（种子只含 python 科目）。
- 忘记 `.venv` 直接用系统 python 可能导致缺依赖或版本不符——统一用 `backend/.venv/Scripts/python`。
- 改动解锁/星级/删除逻辑后务必跑 `tests/test_game_admin.py`（多处分摊实现，易回归）。
- 无 git 仓库：需要版本管理时先 `git init` 并排除 `.venv/ node_modules/ *.db __pycache__/ .pytest_cache/ .env`。
