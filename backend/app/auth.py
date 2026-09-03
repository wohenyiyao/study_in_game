"""认证：PBKDF2 密码哈希 + HMAC 签名令牌（标准库实现，零第三方依赖）。

SECRET 只从环境变量 LQ_SECRET 读取；未设置时每次启动随机生成
（重启后旧令牌全部失效）。生产/多进程部署必须显式设置同一固定密钥。
"""
import base64, hashlib, hmac, json, os, time, secrets

from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from .database import get_db
from .models import User

# 生产务必用环境变量设置固定密钥（如 python -c "import secrets;print(secrets.token_hex(32))"）
SECRET = os.environ.get("LQ_SECRET") or secrets.token_hex(32)
TOKEN_TTL = 7 * 24 * 3600  # 7 天


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return _b64url(salt) + "." + _b64url(dk)


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_b, dk_b = stored.split(".")
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(),
                                 _b64url_decode(salt_b), 100_000)
        return hmac.compare_digest(dk, _b64url_decode(dk_b))
    except Exception:
        return False


def sign_token(user: User) -> str:
    header = _b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url(json.dumps(
        {"uid": user.id, "role": user.role, "exp": int(time.time()) + TOKEN_TTL},
        separators=(",", ":")).encode())
    sig = _b64url(hmac.new(SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
    return f"{header}.{payload}.{sig}"


def verify_token(token: str) -> dict:
    try:
        header, payload, sig = token.split(".")
        expect = _b64url(hmac.new(SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(expect, sig):
            raise ValueError("bad signature")
        data = json.loads(_b64url_decode(payload))
        if data.get("exp", 0) < time.time():
            raise ValueError("expired")
        return data
    except Exception as exc:
        raise HTTPException(status_code=401, detail="登录已失效，请重新登录") from exc


def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User:
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.split(" ", 1)[1].strip()
    data = verify_token(token)
    user = db.get(User, data.get("uid"))
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user
