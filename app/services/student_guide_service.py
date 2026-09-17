"""学生学习引导 Agent 的业务服务。"""

from fastapi import HTTPException

from app.agents.contracts import (
    StudentGuideQuestion,
    StudentLearningGuideRequest,
    StudentLearningResource,
)
from app.agents.student.registry import student_agent_registry
from app.services.student_learning_service import student_learning_service


class StudentGuideService:
    """组装学生有权访问的上下文并调用学生 Agent。"""

    async def guide(
        self,
        *,
        activity_id: int,
        student_id: int,
        student_message: str,
        question_id: int | None,
    ) -> tuple[str, str, int | None]:
        """返回学生 Agent 的学习引导回复。"""
        activity, resources, questions = (
            await student_learning_service.get_learning_context(
                activity_id=activity_id,
                student_id=student_id,
            )
        )

        current_question = None
        if question_id is not None:
            question = next(
                (item for item in questions if item.id == question_id),
                None,
            )
            if question is None:
                raise HTTPException(
                    status_code=404,
                    detail="Question not found in this activity",
                )
            current_question = StudentGuideQuestion(
                question_id=question.id,
                prompt=question.prompt,
                options=question.options,
            )

        agent_request = StudentLearningGuideRequest(
            activity_id=activity_id,
            activity_title=activity.title,
            learning_objective=activity.learning_objective,
            resources=[
                StudentLearningResource(
                    resource_type=resource.resource_type,
                    title=resource.title,
                    content_data=resource.content_data,
                )
                for resource in resources
            ],
            current_question=current_question,
            student_message=student_message,
        )

        result = await student_agent_registry.get_learning_guide_agent().guide(
            agent_request
        )
        return (
            result.reply,
            result.suggested_action,
            current_question.question_id if current_question is not None else None,
        )


student_guide_service = StudentGuideService()