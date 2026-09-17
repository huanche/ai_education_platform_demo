"""API v1 路由配置。

该模块负责设置主 API 路由器，并包含针对身份验证和聊天机器人功能等不同端点的所有子路由器。
"""

"""API v1 router configuration.

This module sets up the main API router and includes all sub-routers for different
endpoints like authentication and chatbot functionality.
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.chatbot import router as chatbot_router

from app.api.v1.courses import router as courses_router
from app.api.v1.activities import router as activities_router
from app.api.v1.teacher_agents import router as teacher_agents_router
from app.api.v1.student_agents import router as student_agents_router

from app.core.logging import logger

api_router = APIRouter()

# Include routers
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])
api_router.include_router(courses_router, prefix="/courses", tags=["Courses"])
api_router.include_router(activities_router, tags=["Learning Activities"])
api_router.include_router(teacher_agents_router, tags=["Teacher Agents"])
api_router.include_router(student_agents_router, tags=["Student Agents"])

@api_router.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        dict: Health status information.
    """
    logger.info("health_check_called")
    return {"status": "healthy", "version": "1.0.0"}
