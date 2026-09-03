"""测试辅助函数。"""


def register_user(client, email: str, password: str = "test123456") -> dict:
    """send-code(读回显码) → register → 返回鉴权 header。"""
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
