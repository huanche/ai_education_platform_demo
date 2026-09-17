"""学生答题接口的请求与响应模型。"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.base import BaseResponse


class SubmitAnswerRequest(BaseModel):
    """学生提交一道单选题答案。"""

    answer_index: int = Field(..., ge=0)


class SubmissionItem(BaseModel):
    """学生一次答题记录。"""

    id: int
    question_id: int
    answer_index: int
    is_correct: bool
    created_at: datetime


class SubmitAnswerResponse(BaseResponse):
    """学生提交答案后的结果。"""

    submission: SubmissionItem
    explanation: str