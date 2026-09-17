"""学生学习引导 Agent 的接口模型。"""

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.base import BaseResponse


class StudentGuideRequest(BaseModel):
    """学生向学习引导 Agent 发送的消息。"""

    student_message: str = Field(..., min_length=1, max_length=3000)
    question_id: int | None = Field(default=None, ge=1)


class StudentGuideResponse(BaseResponse):
    """学生学习引导 Agent 的回复。"""

    reply: str
    suggested_action: Literal["explain", "answer_question", "encourage"]
    current_question_id: int | None