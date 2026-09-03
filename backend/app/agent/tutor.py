"""AI 助教 —— 【Agent 开发位，留给你练手】。

当前实现：返回一个固定回复，保证前端「问助教」面板可用；
你的任务是把它替换成 LangGraph Agent（参考 learn-quest 根目录 AGENT_TODO.md）。

替换后该函数应做到：
1. 接收用户问题 + 用户闯关上下文（progress 摘要 / level 内容）
2. 通过工具获取实时数据：get_user_progress / get_level_info / search_knowledge / give_hint
3. 用 LangGraph create_agent（或你学的多 Agent 结构）编排，
   返回个性化的中文讲解/渐进提示
"""
from sqlalchemy.orm import Session

from ..models import User, Level, Progress


def collect_context(db: Session, user: User, level_id: int | None) -> dict:
    """给 Agent 用的上下文素材（不调 LLM，纯查询）。"""
    cleared = (db.query(Progress).filter(
        Progress.user_id == user.id, Progress.cleared == 1).count())
    level = db.get(Level, level_id) if level_id else None
    return {
        "user_email": user.email,
        "cleared_levels": cleared,
        "current_level": level.title if level else None,
    }


def handle_chat(db: Session, user: User, message: str,
                level_id: int | None) -> tuple[str, bool]:
    """助教聊天入口。返回 (reply, agent_ready)。

    TODO(你来实现):
    - 在这里接 LangGraph Agent，示例流程见 AGENT_TODO.md
    - agent_ready 置 True 表示已接入真实 Agent
    """
    ctx = collect_context(db, user, level_id)
    return (
        f"（AI 助教尚未接入 —— 这是留给你练手的 Agent 开发位）\n"
        f"你已通关 {ctx['cleared_levels']} 关"
        f"{'，当前关卡：' + ctx['current_level'] if ctx['current_level'] else ''}。\n"
        f"你的问题：{message}\n\n"
        f"实现提示：打开 backend/app/agent/ 与项目根 AGENT_TODO.md，"
        f"用 LangGraph 把这里替换成真正的 Agent 吧！",
        False,
    )
