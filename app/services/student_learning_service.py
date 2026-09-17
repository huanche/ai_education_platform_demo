"""学生学习上下文查询服务。"""

from sqlmodel import Session, select

from app.models.learning_activity import LearningActivity
from app.models.learning_resource import LearningResource
from app.models.question import Question
from app.services.activity_service import activity_service
from app.services.database import database_service


class StudentLearningService:
    """为已选课学生提供已发布活动的学习上下文。"""

    async def get_learning_context(
        self,
        *,
        activity_id: int,
        student_id: int,
    ) -> tuple[LearningActivity, list[LearningResource], list[Question]]:
        """返回学生有权学习的活动、资源和题目。"""
        activity = await activity_service.get_published_activity_for_student(
            activity_id=activity_id,
            student_id=student_id,
        )

        with Session(database_service.engine) as session:
            resources_statement = (
                select(LearningResource)
                .where(LearningResource.activity_id == activity_id)
                .order_by(LearningResource.created_at.asc())
            )
            questions_statement = (
                select(Question)
                .where(Question.activity_id == activity_id)
                .order_by(Question.order_index.asc())
            )

            resources = list(session.exec(resources_statement).all())
            questions = list(session.exec(questions_statement).all())

            return activity, resources, questions


student_learning_service = StudentLearningService()