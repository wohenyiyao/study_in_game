"""QQ 邮箱 SMTP 发信（标准库 smtplib，零依赖）。

凭据只从环境变量读取（代码不内置任何默认账号/授权码，避免泄露）：
    LQ_MAIL_HOST=smtp.qq.com  LQ_MAIL_PORT=465
    LQ_MAIL_USER=发信QQ邮箱     LQ_MAIL_CODE=SMTP授权码（不是QQ密码）
    LQ_MAIL_FROM=显示发件人（默认同发信邮箱）
未配置 LQ_MAIL_USER / LQ_MAIL_CODE 时调用会直接抛错。
"""
import os
import smtplib
import ssl
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr

_HOST = os.environ.get("LQ_MAIL_HOST", "smtp.qq.com")
_PORT = int(os.environ.get("LQ_MAIL_PORT", "465"))
_USER = os.environ.get("LQ_MAIL_USER", "")
_CODE = os.environ.get("LQ_MAIL_CODE", "")
_FROM = os.environ.get("LQ_MAIL_FROM", _USER)


def send_code_email(to_email: str, code: str) -> None:
    """发送 6 位验证码邮件；失败抛异常由调用方处理。"""
    if not (_USER and _CODE):
        raise RuntimeError(
            "未配置发信邮箱：请在环境变量设置 LQ_MAIL_USER / LQ_MAIL_CODE"
            "（QQ 邮箱 SMTP 授权码），参考 backend/.env.example")
    subject = "【Python 闯关学】邮箱验证码"
    body = (f"你的注册验证码是：{code}\n"
            f"10 分钟内有效，请勿泄露给他人。\n\n"
            f"（若你未在本站注册，请忽略此邮件）")
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = formataddr((str(Header("Python 闯关学", "utf-8")), _FROM))
    msg["To"] = to_email

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(_HOST, _PORT, context=ctx, timeout=15) as server:
        server.login(_USER, _CODE)
        server.sendmail(_FROM, [to_email], msg.as_string())
