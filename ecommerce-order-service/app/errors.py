import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("ecommerce")


class ApiError(Exception):
    """业务异常：统一转换为 {code, message, data} 结构。"""

    def __init__(self, status_code: int, code: int, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


def ok(data=None, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def handle_api_error(_request: Request, exc: ApiError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message, "data": None},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_request: Request, exc: RequestValidationError):
        details = []
        for item in exc.errors():
            location = ".".join(str(part) for part in item.get("loc", []) if part != "body")
            details.append({"field": location, "message": item.get("msg", "")})
        return JSONResponse(
            status_code=400,
            content={
                "code": 4001,
                "message": "请求参数校验失败：" + "; ".join(
                    f"{d['field']} {d['message']}" for d in details
                ),
                "data": details,
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(_request: Request, exc: Exception):
        logger.exception("unexpected error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"code": 5000, "message": "服务器内部错误", "data": None},
        )
