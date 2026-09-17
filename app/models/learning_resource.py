"""Learning resource database model."""

from typing import Any

from sqlalchemy import JSON, CheckConstraint, Column
from sqlmodel import Field

from app.models.base import BaseModel


class LearningResource(BaseModel, table=True):
    """A teacher-reviewed resource attached to a learning activity."""

    __tablename__ = "learning_resource"

    __table_args__ = (
        CheckConstraint(
            "resource_type IN ('ppt_outline', 'video_script', 'video', 'document')",
            name="ck_learning_resource_type",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="learning_activity.id", index=True)
    created_by: int = Field(foreign_key="user.id", index=True)
    generated_by_task_id: int | None = Field(
        default=None,
        foreign_key="agent_task.id",
        index=True,
    )

    resource_type: str = Field(max_length=30)
    title: str = Field(max_length=120)
    content_data: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    asset_url: str | None = Field(default=None, max_length=2048)
