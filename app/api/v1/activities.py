"""Learning activity API endpoints."""

from fastapi import APIRouter, Depends, Request, status

from app.api.v1.auth import require_student, require_teacher
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import logger
from app.models.learning_activity import LearningActivity
from app.models.user import User
from app.models.learning_resource import LearningResource
from app.models.question import Question

from app.schemas.activity import (
    ActivityCreate,
    ActivityItem,
    ActivityListResponse,
    ActivityResponse,
)
from app.schemas.student_learning import (
    StudentLearningContextResponse,
    StudentLearningResourceItem,
    StudentQuestionItem,
)
from app.services.activity_service import activity_service
from app.services.student_learning_service import student_learning_service

router = APIRouter()


def to_activity_item(activity: LearningActivity) -> ActivityItem:
    """Convert a database activity to API output."""
    if activity.id is None:
        raise RuntimeError("Activity must be persisted before serialization")

    return ActivityItem(
        id=activity.id,
        course_id=activity.course_id,
        title=activity.title,
        description=activity.description,
        learning_objective=activity.learning_objective,
        status=activity.status,
        published_at=activity.published_at,
        created_at=activity.created_at,
    )

def to_student_learning_resource_item(
    resource: LearningResource,
) -> StudentLearningResourceItem:
    """将资源转换为学生可读取的学习资源。"""
    if resource.id is None:
        raise RuntimeError("Learning resource must be persisted before serialization")

    return StudentLearningResourceItem(
        id=resource.id,
        resource_type=resource.resource_type,
        title=resource.title,
        content_data=resource.content_data,
        asset_url=resource.asset_url,
    )


def to_student_question_item(question: Question) -> StudentQuestionItem:
    """将题目转换为学生可作答的题目，不暴露答案。"""
    if question.id is None:
        raise RuntimeError("Question must be persisted before serialization")

    return StudentQuestionItem(
        id=question.id,
        prompt=question.prompt,
        options=question.options,
        order_index=question.order_index,
    )

@router.post(
    "/courses/{course_id}/activities",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["activity_create"][0])
async def create_activity(
    request: Request,
    course_id: int,
    activity_data: ActivityCreate,
    teacher: User = Depends(require_teacher),
) -> ActivityResponse:
    """Create an activity draft in a teacher-owned course."""
    activity = await activity_service.create_activity(
        course_id=course_id,
        teacher_id=teacher.id,
        title=activity_data.title.strip(),
        description=activity_data.description.strip(),
        learning_objective=activity_data.learning_objective.strip(),
    )
    logger.info("learning_activity_created", activity_id=activity.id, course_id=course_id)
    return ActivityResponse(activity=to_activity_item(activity))


@router.get(
    "/courses/{course_id}/activities/mine",
    response_model=ActivityListResponse,
)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["activity_list"][0])
async def get_teacher_activities(
    request: Request,
    course_id: int,
    teacher: User = Depends(require_teacher),
) -> ActivityListResponse:
    """Return all activities, including drafts, for the course teacher."""
    activities = await activity_service.get_teacher_activities(
        course_id=course_id,
        teacher_id=teacher.id,
    )
    return ActivityListResponse(
        activities=[to_activity_item(activity) for activity in activities],
    )


@router.patch(
    "/activities/{activity_id}/publish",
    response_model=ActivityResponse,
)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["activity_publish"][0])
async def publish_activity(
    request: Request,
    activity_id: int,
    teacher: User = Depends(require_teacher),
) -> ActivityResponse:
    """Publish an activity owned by the current teacher."""
    activity = await activity_service.publish_activity(
        activity_id=activity_id,
        teacher_id=teacher.id,
    )
    logger.info("learning_activity_published", activity_id=activity.id, teacher_id=teacher.id)
    return ActivityResponse(activity=to_activity_item(activity))


@router.get(
    "/activities/{activity_id}",
    response_model=ActivityResponse,
)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["activity_read"][0])
async def get_published_activity(
    request: Request,
    activity_id: int,
    student: User = Depends(require_student),
) -> ActivityResponse:
    """Return a published activity to an enrolled student."""
    activity = await activity_service.get_published_activity_for_student(
        activity_id=activity_id,
        student_id=student.id,
    )
    return ActivityResponse(activity=to_activity_item(activity))


@router.get(
    "/activities/{activity_id}/learning-context",
    response_model=StudentLearningContextResponse,
)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["student_learning_context"][0])
async def get_student_learning_context(
    request: Request,
    activity_id: int,
    student: User = Depends(require_student),
) -> StudentLearningContextResponse:
    """返回学生有权学习的已发布活动上下文。"""
    activity, resources, questions = (
        await student_learning_service.get_learning_context(
            activity_id=activity_id,
            student_id=student.id,
        )
    )

    return StudentLearningContextResponse(
        activity=to_activity_item(activity),
        resources=[
            to_student_learning_resource_item(resource)
            for resource in resources
        ],
        questions=[
            to_student_question_item(question)
            for question in questions
        ],
    )