"""AI 助教（Agent 开发位）占位实现单测。"""
from tests.helpers import register_user


def test_assistant_stub_returns_placeholder(client):
    h = register_user(client, "a1@qq.com")
    r = client.post("/api/assistant/chat",
                    json={"message": "什么是变量？", "level_id": 1}, headers=h)
    assert r.status_code == 200
    j = r.json()
    assert j["agent_ready"] is False
    assert "Agent" in j["reply"] or "agent" in j["reply"] or "练手" in j["reply"]


def test_assistant_requires_login(client):
    r = client.post("/api/assistant/chat", json={"message": "hi"})
    assert r.status_code in (401, 403)
