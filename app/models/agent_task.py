"""Agent task database model."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, CheckConstraint, Column
from sqlmodel import Field

from app.models.agent_task_status import QUEUED
from app.models.base import BaseModel


class AgentTask(BaseModel, table=True):
    """A teacher-requested content generation task."""

    __tablename__ = "agent_task"

    __table_args__ = (
        CheckConstraint(
            "status IN ('queued', 'running', 'succeeded', 'failed')",
            name="ck_agent_task_status",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    task_type: str = Field(index=True, max_length=50)
    status: str = Field(default=QUEUED, index=True, max_length=20)

    creator_id: int = Field(foreign_key="user.id", index=True)
    course_id: int = Field(foreign_key="course.id", index=True)
    activity_id: int | None = Field(default=None, foreign_key="learning_activity.id", index=True)

    input_data: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    result_data: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    error_message: str | None = Field(default=None, max_length=2000)
    finished_at: datetime | None = Field(default=None)
