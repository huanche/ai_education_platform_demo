"""教师 Agent API 接口。"""

from fastapi import APIRouter, Depends, Request

from app.api.v1.auth import require_teacher
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import logger
from app.models.agent_task import AgentTask
from app.models.question import Question
from app.models.user import User

from app.models.learning_resource import LearningResource

from app.schemas.teacher_agent import (
    AgentTaskItem,
    GenerateQuestionsRequest,
    GenerateQuestionsResponse,
    TeacherQuestionPreview,
    GeneratePptOutlineRequest,
    GeneratePptOutlineResponse,
    LearningResourceItem,
)
from app.services.teacher_question_task_service import teacher_question_task_service

from app.services.teacher_ppt_task_service import teacher_ppt_task_service

router = APIRouter()


def to_task_item(task: AgentTask) -> AgentTaskItem:
    """将任务模型转换为接口响应。"""
    if task.id is None:
        raise RuntimeError("Agent task must be persisted before serialization")

    return AgentTaskItem(
        id=task.id,
        task_type=task.task_type,
        status=task.status,
        created_at=task.created_at,
        finished_at=task.finished_at,
    )


def to_question_preview(question: Question) -> TeacherQuestionPreview:
    """将题目模型转换为教师预览结果。"""
    if question.id is None:
        raise RuntimeError("Question must be persisted before serialization")

    return TeacherQuestionPreview(
        id=question.id,
        prompt=question.prompt,
        options=question.options,
        correct_option_index=question.correct_option_index,
        explanation=question.explanation,
        order_index=question.order_index,
    )

def to_learning_resource_item(resource: LearningResource) -> LearningResourceItem:
    """将学习资源模型转换为接口响应。"""
    if resource.id is None:
        raise RuntimeError("Learning resource must be persisted before serialization")

    return LearningResourceItem(
        id=resource.id,
        activity_id=resource.activity_id,
        resource_type=resource.resource_type,
        title=resource.title,
        content_data=resource.content_data,
        asset_url=resource.asset_url,
        created_at=resource.created_at,
    )

@router.post(
    "/activities/{activity_id}/generate-questions",
    response_model=GenerateQuestionsResponse,
)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["teacher_question_generate"][0])
async def generate_questions(
    request: Request,
    activity_id: int,
    generation_request: GenerateQuestionsRequest,
    teacher: User = Depends(require_teacher),
) -> GenerateQuestionsResponse:
    """调用教师题库 Agent，为草稿活动生成题目。"""
    task, questions = await teacher_question_task_service.generate_questions(
        activity_id=activity_id,
        teacher_id=teacher.id,
        question_count=generation_request.question_count,
        difficulty=generation_request.difficulty,
        source_material=generation_request.source_material,
    )

    logger.info(
        "teacher_question_generation_succeeded",
        task_id=task.id,
        activity_id=activity_id,
        teacher_id=teacher.id,
        question_count=len(questions),
    )

    return GenerateQuestionsResponse(
        task=to_task_item(task),
        questions=[to_question_preview(question) for question in questions],
    )


@router.post(
    "/activities/{activity_id}/generate-ppt-outline",
    response_model=GeneratePptOutlineResponse,
)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["teacher_ppt_outline_generate"][0])
async def generate_ppt_outline(
    request: Request,
    activity_id: int,
    generation_request: GeneratePptOutlineRequest,
    teacher: User = Depends(require_teacher),
) -> GeneratePptOutlineResponse:
    """调用教师 PPT 大纲 Agent，为草稿活动生成学习资源。"""
    task, resource = await teacher_ppt_task_service.generate_outline(
        activity_id=activity_id,
        teacher_id=teacher.id,
        slide_count=generation_request.slide_count,
        source_material=generation_request.source_material,
    )

    logger.info(
        "teacher_ppt_outline_generation_succeeded",
        task_id=task.id,
        resource_id=resource.id,
        activity_id=activity_id,
        teacher_id=teacher.id,
    )

    return GeneratePptOutlineResponse(
        task=to_task_item(task),
        resource=to_learning_resource_item(resource),
    )