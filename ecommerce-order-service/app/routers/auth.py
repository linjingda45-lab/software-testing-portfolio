from fastapi import APIRouter, Depends

from ..errors import ok
from ..schemas import LoginRequest
from ..security import login, require_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login")
def do_login(body: LoginRequest):
    """登录成功后返回访问令牌，后续下单/查单需携带 Authorization 头。"""
    return ok(login(body.username, body.password))


@router.get("/profile")
def profile(user: dict = Depends(require_user)):
    return ok(user)
