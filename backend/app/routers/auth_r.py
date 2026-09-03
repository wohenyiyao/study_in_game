"""认证路由：发验证码 / 注册（邮箱+验证码）/ 登录（邮箱+密码）/ 当前用户。

流程（已按需求确认）：
- 注册：输入 QQ 邮箱 → 点「发送验证码」→ 邮箱收 6 位码 → 填码+设密码 → 注册成功自动登录
- 登录：QQ 邮箱 + 密码

验证码存储：Redis（原生 TTL 自动过期，一次使用即删，60s 限流用 INCR）。
"""
import hashlib
import random
import os as _os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import SendCodeIn, SendCodeOut, RegisterIn, LoginIn, LoginOut, UserOut
from ..auth import hash_password, verify_password, sign_token, get_current_user
from ..emailer import send_code_email
from ..redis_client import client as redis

router = APIRouter(prefix="/api/auth", tags=["auth"])

CODE_TTL_SECONDS = 600          # 验证码 10 分钟有效
RESEND_SECONDS = 60             # 同一邮箱 60 秒内不可重发
DEV_ECHO = _os.environ.get("LQ_DEV_ECHO_CODE") == "1"   # 开发联调：回显验证码

_PREFIX = "lq:code:"            # 验证码 key 前缀（值 = code 的 sha256）
_RL_PREFIX = "lq:rl:"           # 限流 key 前缀（INCR 计数）


def _code_hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _key(email: str) -> str:
    return _PREFIX + email


def _valid_email(email: str) -> bool:
    email = email.strip().lower()
    return "@" in email and "." in email.split("@")[-1] and len(email) <= 120


def _redis_ready() -> bool:
    try:
        return bool(redis.ping())
    except Exception:
        return False


@router.post("/send-code", response_model=SendCodeOut)
def send_code(body: SendCodeIn, db: Session = Depends(get_db)):
    if not _redis_ready():
        raise HTTPException(503, "验证码服务不可用，请稍后再试")
    email = body.email.strip().lower()
    if not _valid_email(email):
        raise HTTPException(400, "邮箱格式不正确（建议使用 QQ 邮箱）")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "该邮箱已注册，请直接登录")

    # 60 秒限流：INCR 原子计数，首次设置过期
    rl_key = _RL_PREFIX + email
    n = redis.incr(rl_key)
    if n == 1:
        redis.expire(rl_key, RESEND_SECONDS)
    else:
        raise HTTPException(429, "发送过于频繁，请 60 秒后再试")

    code = f"{random.randint(0, 999999):06d}"
    redis.set(_key(email), _code_hash(code), ex=CODE_TTL_SECONDS)
    if DEV_ECHO:
        # 本地联调（LQ_DEV_ECHO_CODE=1）：代码不内置 SMTP 凭据，跳过真实发信，直接回显验证码
        return SendCodeOut(msg="验证码已发送", dev_code=code)
    try:
        send_code_email(email, code)
    except Exception as exc:
        redis.delete(_key(email))  # 发信失败，作废验证码
        raise HTTPException(502, f"验证码发送失败：{exc}") from exc
    return SendCodeOut(msg="验证码已发送", dev_code=None)


def _verify_code(email: str, code: str) -> None:
    """校验：存在（未过期，Redis TTL 自动处理）→ 匹配 → 删除（一次性）。"""
    stored = redis.get(_key(email))
    if stored is None:
        raise HTTPException(400, "验证码不存在或已过期，请重新获取")
    if stored != _code_hash(code.strip()):
        raise HTTPException(400, "验证码错误")
    redis.delete(_key(email))


@router.post("/register", response_model=LoginOut)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if not _redis_ready():
        raise HTTPException(503, "验证码服务不可用，请稍后再试")
    email = body.email.strip().lower()
    if not _valid_email(email):
        raise HTTPException(400, "邮箱格式不正确")
    if len(body.password) < 6:
        raise HTTPException(400, "密码至少 6 位")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "该邮箱已注册")
    if not body.code:
        raise HTTPException(400, "请填写邮箱验证码")
    _verify_code(email, body.code)

    user = User(email=email, password_hash=hash_password(body.password), role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    return LoginOut(token=sign_token(user), user=UserOut.model_validate(user))


@router.post("/login", response_model=LoginOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    email = body.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(400, "邮箱或密码错误")
    return LoginOut(token=sign_token(user), user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)
