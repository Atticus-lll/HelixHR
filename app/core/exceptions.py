from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppException(Exception):
    def __init__(
        self,
        status_code: int = 400,
        message: str = "业务异常",
        code: str | None = None,
        data: Any = None,
    ):
        self.status_code = status_code
        self.message = message
        self.code = code or str(status_code)
        self.data = data
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(status_code=404, message=message)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "未授权"):
        super().__init__(status_code=401, message=message)


class ForbiddenException(AppException):
    def __init__(self, message: str = "权限不足"):
        super().__init__(status_code=403, message=message)


class ConflictException(AppException):
    def __init__(self, message: str = "资源冲突"):
        super().__init__(status_code=409, message=message)


class ValidationException(AppException):
    def __init__(self, message: str = "参数校验失败"):
        super().__init__(status_code=422, message=message)


def api_response(
    data: Any = None,
    message: str = "操作成功",
    code: int = 200,
) -> dict[str, Any]:
    return {"code": code, "message": message, "data": data}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=api_response(data=None, message=str(exc.detail), code=exc.status_code),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=api_response(
                data={"errors": exc.errors()},
                message="请求参数校验失败",
                code=422,
            ),
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content=api_response(data=exc.data, message=exc.message, code=exc.status_code),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        import traceback
        content = api_response(data=None, message="服务器内部错误", code=500)
        if app.debug:
            content["data"] = {"error": str(exc), "trace": traceback.format_exc()}
        return JSONResponse(status_code=500, content=content)
