"""Course and enrollment API endpoints."""

from fastapi import APIRouter, Depends, Request, status

from app.api.v1.auth import require_student, require_teacher
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import logger
from app.models.user import User
from app.schemas.course import (
    CourseCreate,
    CourseItem,
    CourseListResponse,
    CourseResponse,
    EnrollmentResponse,
)
from app.services.course_service import course_service

router = APIRouter()


def to_course_item(course) -> CourseItem:
    """Convert a Course model to its API representation."""
    return CourseItem(
        id=course.id,
        title=course.title,
        description=course.description,
        teacher_id=course.teacher_id,
        created_at=course.created_at,
    )


@router.post(
    "",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["course_create"][0])
async def create_course(
    request: Request,
    course_data: CourseCreate,
    teacher: User = Depends(require_teacher),
) -> CourseResponse:
    """Create a course for the authenticated teacher."""
    course = await course_service.create_course(
        teacher_id=teacher.id,
        title=course_data.title.strip(),
        description=course_data.description.strip(),
    )
    logger.info("course_created", course_id=course.id, teacher_id=teacher.id)
    return CourseResponse(course=to_course_item(course))


@router.get("/mine", response_model=CourseListResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["course_list"][0])
async def get_my_courses(
    request: Request,
    teacher: User = Depends(require_teacher),
) -> CourseListResponse:
    """Return courses created by the authenticated teacher."""
    courses = await course_service.get_courses_by_teacher(teacher.id)
    return CourseListResponse(courses=[to_course_item(course) for course in courses])


@router.post(
    "/{course_id}/enroll",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["course_enroll"][0])
async def enroll_in_course(
    request: Request,
    course_id: int,
    student: User = Depends(require_student),
) -> EnrollmentResponse:
    """Enroll the authenticated student in a course."""
    enrollment = await course_service.enroll_student(
        course_id=course_id,
        student_id=student.id,
    )
    logger.info(
        "student_enrolled_in_course",
        course_id=course_id,
        student_id=student.id,
    )
    return EnrollmentResponse(
        course_id=enrollment.course_id,
        student_id=enrollment.student_id,
        created_at=enrollment.created_at,
    )


@router.get("/enrolled", response_model=CourseListResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["course_list"][0])
async def get_enrolled_courses(
    request: Request,
    student: User = Depends(require_student),
) -> CourseListResponse:
    """Return courses joined by the authenticated student."""
    courses = await course_service.get_courses_for_student(student.id)
    return CourseListResponse(courses=[to_course_item(course) for course in courses])
