"""教师与学生 Agent 的统一输入输出契约。"""

from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field, model_validator


class QuestionDraft(BaseModel):
    """教师 Agent 生成的一道单选题草稿。"""

    prompt: str = Field(..., min_length=1, max_length=3000)
    options: list[str] = Field(..., min_length=2, max_length=6)
    correct_option_index: int = Field(..., ge=0)
    explanation: str = Field(default="", max_length=3000)

    @model_validator(mode="after")
    def validate_correct_option_index(self) -> "QuestionDraft":
        """确保正确答案索引位于选项范围内。"""
        if self.correct_option_index >= len(self.options):
            raise ValueError("correct_option_index must reference an existing option")
        return self


class QuestionBankGenerationRequest(BaseModel):
    """平台传递给教师题库 Agent 的生成请求。"""

    course_id: int
    activity_id: int
    activity_title: str = Field(..., min_length=1, max_length=120)
    learning_objective: str = Field(default="", max_length=1000)
    question_count: int = Field(..., ge=1, le=3)
    difficulty: Literal["beginner", "intermediate", "advanced"]
    source_material: str = Field(..., min_length=20, max_length=12000)


class QuestionBankGenerationResult(BaseModel):
    """教师题库 Agent 返回的结构化生成结果。"""

    questions: list[QuestionDraft]


class TeacherQuestionBankAgent(Protocol):
    """教师题库 Agent 必须实现的能力接口。"""

    async def generate(
        self,
        request: QuestionBankGenerationRequest,
    ) -> QuestionBankGenerationResult:
        """根据教学目标生成题目草稿。"""

class PptOutlineSlide(BaseModel):
    """教师 PPT 大纲中的单页内容。"""

    title: str = Field(..., min_length=1, max_length=120)
    key_points: list[str] = Field(..., min_length=2, max_length=6)
    speaker_notes: str = Field(default="", max_length=2000)


class PptOutlineGenerationRequest(BaseModel):
    """传递给教师 PPT 大纲 Agent 的生成请求。"""

    course_id: int
    activity_id: int
    activity_title: str = Field(..., min_length=1, max_length=120)
    learning_objective: str = Field(default="", max_length=1000)
    slide_count: int = Field(..., ge=3, le=12)
    source_material: str = Field(..., min_length=20, max_length=12000)


class PptOutlineGenerationResult(BaseModel):
    """教师 PPT 大纲 Agent 返回的结构化结果。"""

    slides: list[PptOutlineSlide]


class TeacherPptOutlineAgent(Protocol):
    """教师 PPT 大纲 Agent 必须实现的能力接口。"""

    async def generate(
        self,
        request: PptOutlineGenerationRequest,
    ) -> PptOutlineGenerationResult:
        """根据教学资料生成 PPT 大纲。"""
class StudentLearningResource(BaseModel):
    """学生 Agent 可读取的已发布学习资源。"""

    resource_type: str
    title: str
    content_data: dict[str, Any] | None


class StudentGuideQuestion(BaseModel):
    """学生 Agent 当前引导的题目。"""

    question_id: int
    prompt: str
    options: list[str]


class StudentLearningGuideRequest(BaseModel):
    """传递给学生学习引导 Agent 的请求。"""

    activity_id: int
    activity_title: str
    learning_objective: str
    resources: list[StudentLearningResource]
    current_question: StudentGuideQuestion | None = None
    student_message: str = Field(..., min_length=1, max_length=3000)


class StudentLearningGuideResult(BaseModel):
    """学生学习引导 Agent 的结构化回复。"""

    reply: str = Field(..., min_length=1, max_length=3000)
    suggested_action: Literal["explain", "answer_question", "encourage"]


class StudentLearningGuideAgent(Protocol):
    """学生学习引导 Agent 的能力接口。"""

    async def guide(
        self,
        request: StudentLearningGuideRequest,
    ) -> StudentLearningGuideResult:
        """根据已发布资料引导学生学习。"""
        ...
