"""教师题库 Agent 任务编排与题目保存服务。"""

from datetime import UTC, datetime

from fastapi import HTTPException
from sqlmodel import Session, delete

from app.agents.contracts import QuestionBankGenerationRequest
from app.agents.teacher.registry import teacher_agent_registry
from app.core.logging import logger
from app.models.activity_status import DRAFT
from app.models.agent_task import AgentTask
from app.models.agent_task_status import FAILED, QUEUED, RUNNING, SUCCEEDED
from app.models.course import Course
from app.models.learning_activity import LearningActivity
from app.models.question import Question
from app.services.database import database_service

QUESTION_BANK_TASK_TYPE = "question_bank_generator"


class TeacherQuestionTaskService:
    """处理教师发起的题库生成任务。"""

    async def generate_questions(
        self,
        *,
        activity_id: int,
        teacher_id: int,
        question_count: int,
        difficulty: str,
        source_material: str,
    ) -> tuple[AgentTask, list[Question]]:
        """创建任务、调用教师 Agent，并保存题目草稿。"""
        task_id, course_id, activity_title, learning_objective = self._create_task(
            activity_id=activity_id,
            teacher_id=teacher_id,
            question_count=question_count,
            difficulty=difficulty,
            source_material=source_material,
        )

        if task_id is None:
            raise RuntimeError("Agent task must be persisted before execution")

        self._mark_task_running(task_id)

        try:
            agent_request = QuestionBankGenerationRequest(
                course_id=course_id,
                activity_id=activity_id,
                activity_title=activity_title,
                learning_objective=learning_objective,
                question_count=question_count,
                difficulty=difficulty,
                source_material=source_material,
            )
            agent = teacher_agent_registry.get_question_bank_agent()
            result = await agent.generate(agent_request)

            return self._save_generated_questions(
                task_id=task_id,
                activity_id=activity_id,
                teacher_id=teacher_id,
                questions=result.questions,
            )
        except Exception as error:
            self._mark_task_failed(task_id, error)
            logger.exception(
                "teacher_question_generation_failed",
                task_id=task_id,
                activity_id=activity_id,
                teacher_id=teacher_id,
                error=str(error),
            )
            raise

    def _create_task(
        self,
        *,
        activity_id: int,
        teacher_id: int,
        question_count: int,
        difficulty: str,
        source_material: str,
    ) -> tuple[int, int, str, str]:
        """校验教师权限并创建排队中的任务。"""
        with Session(database_service.engine) as session:
            activity = session.get(LearningActivity, activity_id)
            if activity is None:
                raise HTTPException(status_code=404, detail="Activity not found")

            course = session.get(Course, activity.course_id)
            if course is None or course.teacher_id != teacher_id:
                raise HTTPException(
                    status_code=403,
                    detail="Cannot generate questions for another teacher's activity",
                )

            if activity.status != DRAFT:
                raise HTTPException(
                    status_code=409,
                    detail="Questions can only be generated for a draft activity",
                )

            task = AgentTask(
                task_type=QUESTION_BANK_TASK_TYPE,
                status=QUEUED,
                creator_id=teacher_id,
                course_id=activity.course_id,
                activity_id=activity.id,
                input_data={
                    "question_count": question_count,
                    "difficulty": difficulty,
                    "source_material": source_material,
                },
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            if task.id is None or activity.id is None:
                raise RuntimeError("Task and activity must be persisted before use")

            return (
                task.id,
                activity.course_id,
                activity.title,
                activity.learning_objective,
            )

    def _mark_task_running(self, task_id: int) -> None:
        """将任务更新为执行中。"""
        with Session(database_service.engine) as session:
            task = session.get(AgentTask, task_id)
            if task is None:
                raise RuntimeError("Agent task not found")

            task.status = RUNNING
            session.add(task)
            session.commit()

    def _save_generated_questions(
        self,
        *,
        task_id: int,
        activity_id: int,
        teacher_id: int,
        questions: list,
    ) -> tuple[AgentTask, list[Question]]:
        """替换草稿活动题目，并将任务标记为成功。"""
        with Session(database_service.engine) as session:
            activity = session.get(LearningActivity, activity_id)
            if activity is None or activity.status != DRAFT:
                raise HTTPException(
                    status_code=409,
                    detail="Activity is no longer available for question generation",
                )

            course = session.get(Course, activity.course_id)
            if course is None or course.teacher_id != teacher_id:
                raise HTTPException(status_code=403, detail="Teacher permission is no longer valid")

            session.exec(delete(Question).where(Question.activity_id == activity_id))

            saved_questions = [
                Question(
                    activity_id=activity_id,
                    prompt=question.prompt,
                    options=question.options,
                    correct_option_index=question.correct_option_index,
                    explanation=question.explanation,
                    order_index=index,
                )
                for index, question in enumerate(questions)
            ]
            session.add_all(saved_questions)
            session.flush()

            task = session.get(AgentTask, task_id)
            if task is None:
                raise RuntimeError("Agent task not found")

            task.status = SUCCEEDED
            task.result_data = {
                "question_count": len(saved_questions),
                "question_ids": [question.id for question in saved_questions],
            }
            task.finished_at = datetime.now(UTC)

            session.add(task)
            session.commit()

            session.refresh(task)
            for saved_question in saved_questions:
                session.refresh(saved_question)

            return task, saved_questions

    def _mark_task_failed(self, task_id: int, error: Exception) -> None:
        """将失败信息保存到任务记录。"""
        with Session(database_service.engine) as session:
            task = session.get(AgentTask, task_id)
            if task is None:
                return

            task.status = FAILED
            task.error_message = str(error)[:2000]
            task.finished_at = datetime.now(UTC)

            session.add(task)
            session.commit()


teacher_question_task_service = TeacherQuestionTaskService()
