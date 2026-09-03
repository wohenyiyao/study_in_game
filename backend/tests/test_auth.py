"""认证链路单测：验证码(Redis) → 注册 → 登录。"""
from tests.helpers import register_user


def test_register_full_flow(client):
    h = register_user(client, "t1@qq.com")
    me = client.get("/api/auth/me", headers=h)
    assert me.status_code == 200 and me.json()["email"] == "t1@qq.com"
    assert me.json()["role"] == "user"


def test_wrong_code_rejected(client):
    r = client.post("/api/auth/send-code", json={"email": "t2@qq.com"})
    assert r.status_code == 200
    r = client.post("/api/auth/register",
                    json={"email": "t2@qq.com", "password": "test123456", "code": "000000"})
    assert r.status_code == 400
    assert "验证码错误" in r.json()["detail"]


def test_code_is_one_time(client):
    r = client.post("/api/auth/send-code", json={"email": "t3@qq.com"})
    code = r.json()["dev_code"]
    body = {"email": "t3@qq.com", "password": "test123456", "code": code}
    assert client.post("/api/auth/register", json=body).status_code == 200
    # 同一验证码不可二次使用（Redis 已删除）
    assert client.post("/api/auth/register", json=body).status_code == 400


def test_duplicate_email_rejected(client):
    register_user(client, "t4@qq.com")
    r = client.post("/api/auth/send-code", json={"email": "t4@qq.com"})
    assert r.status_code == 400 and "已注册" in r.json()["detail"]


def test_login_ok_and_wrong_password(client):
    register_user(client, "t5@qq.com")
    ok = client.post("/api/auth/login", json={"email": "t5@qq.com", "password": "test123456"})
    assert ok.status_code == 200 and "token" in ok.json()
    bad = client.post("/api/auth/login", json={"email": "t5@qq.com", "password": "wrong-pass"})
    assert bad.status_code == 400


def test_send_code_ratelimit(client):
    client.post("/api/auth/send-code", json={"email": "t6@qq.com"})
    r = client.post("/api/auth/send-code", json={"email": "t6@qq.com"})
    assert r.status_code == 429
