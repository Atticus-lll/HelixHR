from fastapi import APIRouter

from app.api.v1 import auth, departments, employees, rag, roles, salaries

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(employees.router)
api_router.include_router(departments.router)
api_router.include_router(salaries.router)
api_router.include_router(roles.router)
api_router.include_router(rag.router)
