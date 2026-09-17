"""学生学习上下文接口的请求与响应模型。"""

from typing import Any

from pydantic import BaseModel

from app.schemas.activity import ActivityItem
from app.schemas.base import BaseResponse


class StudentLearningResourceItem(BaseModel):
    """学生可阅读的已发布学习资源。"""

    id: int
    resource_type: str
    title: str
    content_data: dict[str, Any] | None
    asset_url: str | None


class StudentQuestionItem(BaseModel):
    """学生可作答的题目，不包含正确答案和解析。"""

    id: int
    prompt: str
    options: list[str]
    order_index: int


class StudentLearningContextResponse(BaseResponse):
    """学生学习页面和学生 Agent 使用的活动上下文。"""

    activity: ActivityItem
    resources: list[StudentLearningResourceItem]
    questions: list[StudentQuestionItem]