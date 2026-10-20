import secrets
from typing import Optional

from fastapi import Header

from .db import query_one
from .errors import ApiError

# 演示项目使用进程内令牌；生产环境可替换为 Redis + JWT
_TOKENS: dict[str, dict] = {}


def login(username: str, password: str) -> dict:
    user = query_one(
        "SELECT id, username, password, nickname, status FROM users WHERE username = %s",
        (username,),
    )
    if user is None or user["password"] != password:
        raise ApiError(401, 1002, "用户名或密码错误")
    if user["status"] != 1:
        raise ApiError(403, 1004, "账号已被禁用")

    token = secrets.token_hex(16)
    profile = {
        "userId": user["id"],
        "username": user["username"],
        "nickname": user["nickname"],
    }
    _TOKENS[token] = profile
    return {"token": token, **profile}


def require_user(authorization: Optional[str] = Header(default=None)) -> dict:
    if not authorization:
        raise ApiError(401, 1003, "未登录或缺少访问令牌")
    token = authorization[7:] if authorization.lower().startswith("bearer ") else authorization
    profile = _TOKENS.get(token.strip())
    if profile is None:
        raise ApiError(401, 1003, "登录状态已失效，请重新登录")
    return profile
