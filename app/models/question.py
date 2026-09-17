"""Question database model."""

from sqlalchemy import JSON, CheckConstraint, Column
from sqlmodel import Field

from app.models.base import BaseModel


class Question(BaseModel, table=True):
    """A single-choice question belonging to a learning activity."""

    __tablename__ = "question"

    __table_args__ = (
        CheckConstraint(
            "correct_option_index >= 0",
            name="ck_question_correct_option_index",
        ),
        CheckConstraint(
            "order_index >= 0",
            name="ck_question_order_index",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="learning_activity.id", index=True)
    prompt: str = Field(max_length=3000)
    options: list[str] = Field(sa_column=Column(JSON, nullable=False))
    correct_option_index: int
    explanation: str = Field(default="", max_length=3000)
    order_index: int = Field(default=0, index=True)
