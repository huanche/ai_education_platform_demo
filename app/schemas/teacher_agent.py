"""教师 Agent 接口的请求与响应模型。"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.base import BaseResponse


class GenerateQuestionsRequest(BaseModel):
    """教师请求题库 Agent 生成题目的参数。"""

    question_count: int = Field(..., ge=1, le=3)
    difficulty: Literal["beginner", "intermediate", "advanced"]
    source_material: str = Field(..., min_length=20, max_length=12000)


class AgentTaskItem(BaseModel):
    """面向教师返回的 Agent 任务摘要。"""

    id: int
    task_type: str
    status: str
    created_at: datetime
    finished_at: datetime | None


class TeacherQuestionPreview(BaseModel):
    """教师预览题目，包含答案与解析。"""

    id: int
    prompt: str
    options: list[str]
    correct_option_index: int
    explanation: str
    order_index: int


class GenerateQuestionsResponse(BaseResponse):
    """教师题库 Agent 的生成结果。"""

    task: AgentTaskItem
    questions: list[TeacherQuestionPreview]

class GeneratePptOutlineRequest(BaseModel):
    """教师请求 PPT 大纲 Agent 的参数。"""

    slide_count: int = Field(..., ge=3, le=12)
    source_material: str = Field(..., min_length=20, max_length=12000)


class LearningResourceItem(BaseModel):
    """面向教师返回的学习资源摘要。"""

    id: int
    activity_id: int
    resource_type: str
    title: str
    content_data: dict[str, Any] | None
    asset_url: str | None
    created_at: datetime


class GeneratePptOutlineResponse(BaseResponse):
    """教师 PPT 大纲 Agent 的生成结果。"""

    task: AgentTaskItem
    resource: LearningResourceItem
