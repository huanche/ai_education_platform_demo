"""Student submission database model."""

from sqlalchemy import CheckConstraint
from sqlmodel import Field

from app.models.base import BaseModel


class Submission(BaseModel, table=True):
    """One student answer attempt for a question."""

    __tablename__ = "submission"

    __table_args__ = (
        CheckConstraint(
            "answer_index >= 0",
            name="ck_submission_answer_index",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="question.id", index=True)
    student_id: int = Field(foreign_key="user.id", index=True)
    answer_index: int
    is_correct: bool
