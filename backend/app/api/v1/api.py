from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .food import router as food_router
from .nutrition import router as nutrition_router
from .dashboard import router as dashboard_router

# Main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(food_router, prefix="/food", tags=["Food"])
api_router.include_router(nutrition_router, prefix="/nutrition", tags=["Nutrition"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
