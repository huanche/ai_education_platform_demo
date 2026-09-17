"""Course database model."""

from sqlmodel import Field

from app.models.base import BaseModel


class Course(BaseModel, table=True):
    """A course created and owned by a teacher."""

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=120)
    description: str = Field(default="", max_length=2000)
    teacher_id: int = Field(foreign_key="user.id", index=True)
