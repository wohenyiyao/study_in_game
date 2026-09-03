# AGENT_TODO.md —— 你的 Agent 练习任务书 🤖

项目所有 CRUD（注册/登录/地图/答题/错题/管理后台 + Vue 前端）已完成并有测试覆盖。
**现在轮到你来把「AI 助教」从占位变成真正的 Agent。**

## 当前状态

`backend/app/agent/tutor.py` 的 `handle_chat()` 目前只返回固定占位文本
（`agent_ready=False`）。前端答题页右下角 🤖 按钮已经接好
`POST /api/assistant/chat`，数据结构也定好了——你只改后端这一个函数（可加文件）。

## 接口契约（已定死，别改前端）

```
POST /api/assistant/chat
入参: {"message": "这道题为什么选 tuple？", "level_id": 1}
出参: {"reply": "AI 助教回复文本", "agent_ready": true}
```

## 需求（建议的分步练习，按你的学习进度递进）

### 阶段 A：单 Agent + 工具（复用你学过的 create_agent）
工具建议（每个都是真实可调用的，务必做成 `@tool`）：
1. `get_user_progress()`：查当前用户通关数/当前关卡/答错题（已通关数等素材在
   `tutor.collect_context` 里已有雏形，升级为工具即可）
2. `get_level_questions(level_id)`：取某关全部题目（含解析）
3. `search_knowledge(query)`：RAG 检索——把种子题的解析/知识点做成可检索的小知识库
   （可直接套用你医疗问答项目里的混合检索代码，换成 Chroma 更轻）
4. `give_hint(level_id)`：返回渐进式提示（不回放答案，先提示思路）

行为要求：答错时**不直接给答案**，先讲知识点、引导再想一次；这是"助教"区别于"抄答案机"的产品价值，也是面试亮点。

### 阶段 B：记忆（你已会 MemorySaver + thread_id）
同一用户连续追问（"那列表推导式呢？"）要记得上文。thread_id 用 `user.id` 即可。
注意：`handle_chat` 是无状态的 HTTP 调用——思考怎么把 LangGraph 检查点接进来
（方案：模块级 compiled agent + 每次 invoke 传 `{"configurable":{"thread_id": uid}}`）。

### 阶段 C（进阶，可选）：多 Agent
参考你的客服项目：supervisor 分流「要提示 / 要讲解 / 闲聊」，再决定调哪个子 Agent。

## 验收清单（做完对照）

- [ ] 输入 "这道题为什么选 tuple？" → 能结合该关题目/解析给出中文讲解
- [ ] 输入 "给个提示" → 返回思路提示而非答案
- [ ] 连续问两句话 → 第二句记得第一句（记忆）
- [ ] 答错记录出现在错题本后，助教能提到"你上次这题答错了"
- [ ] `agent_ready` 置 True；前端 🤖 面板正常对话
- [ ] 你实测过的对话场景，补进 `backend/tests/test_agent.py`（把占位断言改成真实断言）

## 素材提醒

- LLM：本机可用 DeepSeek API（.credentials.yaml 里有 key）或 Ollama qwen2.5:3b（更省）
- 参考代码：`E:\py-workspace\langgraph-study\cs-agent-hub`（你的客服多 Agent 项目）
- 结构参考：`E:\py-workspace\langgraph-study\LangGraph学习清单.ipynb` §7
