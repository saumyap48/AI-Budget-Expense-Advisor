from fastapi import APIRouter
from app.routes.v1.auth import router as auth_router
from app.routes.v1.expenses import router as expenses_router
from app.routes.v1.budgets import router as budgets_router
from app.routes.v1.analytics import router as analytics_router
from app.routes.v1.chat import router as chat_router
from app.routes.v1.health import router as health_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(expenses_router)
api_v1_router.include_router(budgets_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(chat_router)
