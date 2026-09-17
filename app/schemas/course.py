"""Request and response schemas for course endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.base import BaseResponse


class CourseCreate(BaseModel):
    """Request body for a teacher creating a course."""

    title: str = Field(..., min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)


class CourseItem(BaseModel):
    """Course data returned inside API responses."""

    id: int
    title: str
    description: str
    teacher_id: int
    created_at: datetime


class CourseResponse(BaseResponse):
    """Response returned after creating a course."""

    course: CourseItem


class CourseListResponse(BaseResponse):
    """Response containing a list of courses."""

    courses: list[CourseItem]


class EnrollmentResponse(BaseResponse):
    """Response returned after a student enrolls in a course."""

    course_id: int
    student_id: int
    created_at: datetime
