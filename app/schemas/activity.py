"""Request and response schemas for learning activities."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.base import BaseResponse


class ActivityCreate(BaseModel):
    """Request body for creating a learning activity draft."""

    title: str = Field(..., min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    learning_objective: str = Field(default="", max_length=1000)


class ActivityItem(BaseModel):
    """Learning activity data returned by the API."""

    id: int
    course_id: int
    title: str
    description: str
    learning_objective: str
    status: str
    published_at: datetime | None
    created_at: datetime


class ActivityResponse(BaseResponse):
    """Response containing one learning activity."""

    activity: ActivityItem


class ActivityListResponse(BaseResponse):
    """Response containing learning activities."""

    activities: list[ActivityItem]
