"""学生学习引导 Agent API 接口。"""

from fastapi import APIRouter, Depends, Request

from app.api.v1.auth import require_student
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import logger
from app.models.user import User
from app.schemas.student_agent import StudentGuideRequest, StudentGuideResponse
from app.services.student_guide_service import student_guide_service

router = APIRouter()


@router.post(
    "/activities/{activity_id}/learning-guide",
    response_model=StudentGuideResponse,
)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["student_learning_guide"][0])
async def guide_student_learning(
    request: Request,
    activity_id: int,
    guide_request: StudentGuideRequest,
    student: User = Depends(require_student),
) -> StudentGuideResponse:
    """调用学生学习引导 Agent。"""
    reply, suggested_action, current_question_id = (
        await student_guide_service.guide(
            activity_id=activity_id,
            student_id=student.id,
            student_message=guide_request.student_message,
            question_id=guide_request.question_id,
        )
    )

    logger.info(
        "student_learning_guidance_succeeded",
        activity_id=activity_id,
        student_id=student.id,
        current_question_id=current_question_id,
        suggested_action=suggested_action,
    )

    return StudentGuideResponse(
        reply=reply,
        suggested_action=suggested_action,
        current_question_id=current_question_id,
    )