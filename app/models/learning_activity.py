"""Learning activity database model."""

from datetime import datetime

from sqlalchemy import CheckConstraint
from sqlmodel import Field

from app.models.activity_status import DRAFT
from app.models.base import BaseModel


class LearningActivity(BaseModel, table=True):
    """A teacher-created learning activity within a course."""

    __tablename__ = "learning_activity"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'published')",
            name="ck_learning_activity_status",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="course.id", index=True)
    title: str = Field(index=True, max_length=120)
    description: str = Field(default="", max_length=2000)
    learning_objective: str = Field(default="", max_length=1000)
    status: str = Field(default=DRAFT, index=True, max_length=20)
    published_at: datetime | None = Field(default=None)
