"""Course enrollment database model."""

from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from app.models.base import BaseModel


class Enrollment(BaseModel, table=True):
    """A student's enrollment in a course."""

    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "student_id",
            name="uq_enrollment_course_student",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="course.id", index=True)
    student_id: int = Field(foreign_key="user.id", index=True)
