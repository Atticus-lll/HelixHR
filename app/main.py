import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.utils.logger import logger

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("启动 {} v{}".format(settings.app.name, settings.app.version))
    logger.info("Debug 模式: {}".format(settings.app.debug))
    yield
    logger.info("应用关闭")


app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    debug=settings.app.debug,
    description=(
        "基于 FastAPI + SQLAlchemy 的 AI 驱动型人力资源系统\n"
        "- 支持 RBAC 权限控制\n"
        "- JWT 认证\n"
        "- RAG 智能知识检索\n"
        "- MySQL 数据库存储\n"
        "- Docker 一键部署"
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


def _clean_openapi_schema(schema: dict) -> dict:
    """移除 OpenAPI schema 中由内部机制注入的假参数"""
    unwanted = {"args", "kwargs"}
    for path, path_item in schema.get("paths", {}).items():
        if isinstance(path_item, dict):
            for method, operation in path_item.items():
                if isinstance(operation, dict) and "parameters" in operation:
                    operation["parameters"] = [
                        p
                        for p in operation["parameters"]
                        if isinstance(p, dict) and p.get("name") not in unwanted
                    ]
    return schema


# 修补 app.openapi() 方法，返回清理后的 schema
_original_openapi = app.openapi


def _patched_openapi():
    schema = _original_openapi()
    return _clean_openapi_schema(schema)


app.openapi = _patched_openapi


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
)


@app.middleware("http")
async def clean_openapi_response(request: Request, call_next):
    """拦截 /openapi.json 响应，清理假参数"""
    response = await call_next(request)
    if request.url.path == "/openapi.json":
        try:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            schema = _clean_openapi_schema(
                __import__("json").loads(body)
            )
            return JSONResponse(content=schema, status_code=response.status_code)
        except Exception:
            pass
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start_time) * 1000, 2)
    logger.info("{} {} - {} - {}ms".format(
        request.method, request.url.path, response.status_code, process_time
    ))
    response.headers["X-Process-Time-Ms"] = str(process_time)
    return response


register_exception_handlers(app)


@app.get("/debug/me-validate", tags=["调试"], include_in_schema=False)
async def debug_me_validate():
    """查看 /me 的 dependant 详情"""
    for route in app.routes:
        if hasattr(route, 'path') and route.path == '/api/v1/auth/me':
            if hasattr(route, 'dependant'):
                dep = route.dependant
                return {
                    "path": route.path,
                    "dependant_call": str(dep.call),
                    "path_params": [(p.name, str(p.field_info)) for p in dep.path_params],
                    "query_params": [(p.name, str(p.field_info)) for p in dep.query_params],
                    "body_params": [(p.name, str(p.field_info)) for p in dep.body_params],
                    "flat_params": [(p.name, str(p.field_info)) for p in dep.flat_params],
                    "security_params": [(p.name, str(p.field_info)) for p in dep.security_params],
                }
            break
    return {"error": "route not found"}


app.include_router(api_router)


@app.get("/", tags=["系统"], responses={200: {"description": "返回系统基本信息"}})
def root():
    return {
        "name": settings.app.name,
        "version": settings.app.version,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["系统"], summary="健康检查", responses={200: {"description": "服务运行正常"}})
def health_check():
    return {
        "status": "ok",
        "service": settings.app.name,
        "version": settings.app.version,
    }


@app.get("/ping", tags=["系统"], summary="心跳检测", responses={200: {"description": "心跳响应正常"}})
def ping():
    return {"message": "pong"}


@app.get("/debug/validate/{path:path}", tags=["调试"], include_in_schema=False)
async def debug_validate(path: str):
    """调试端点：打印原始请求参数和查询参数"""
    for route in app.routes:
        if hasattr(route, 'path') and route.path == f'/{path}':
            if hasattr(route, 'dependant'):
                dep = route.dependant
                return {
                    "path": f'/{path}',
                    "path_params": dep.path_params,
                    "query_params": dep.query_params,
                    "body_params": dep.body_params,
                    "flat_params": dep.flat_params,
                    "security_params": dep.security_params,
                    "dependant": {
                        "call": str(dep.call) if hasattr(dep, 'call') else None,
                    },
                }
            break

    return {"path": f'/{path}', "note": "route not found"}


@app.get("/debug/request", tags=["调试"], include_in_schema=False)
async def debug_request(request: Request):
    """打印所有查询参数"""
    return {
        "query_params": dict(request.query_params),
        "path_params": dict(request.path_params),
        "headers": dict(request.headers),
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app.main:app', host=settings.app.host, port=settings.app.port, reload=settings.app.debug)
