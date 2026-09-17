"""教师 PPT 大纲 Agent 任务编排与资源保存服务。"""

from datetime import UTC, datetime

from fastapi import HTTPException
from sqlmodel import Session, delete

from app.agents.contracts import (
    PptOutlineGenerationRequest,
    PptOutlineSlide,
)
from app.agents.teacher.registry import teacher_agent_registry
from app.core.logging import logger
from app.models.activity_status import DRAFT
from app.models.agent_task import AgentTask
from app.models.agent_task_status import FAILED, QUEUED, RUNNING, SUCCEEDED
from app.models.course import Course
from app.models.learning_activity import LearningActivity
from app.models.learning_resource import LearningResource
from app.services.database import database_service

PPT_OUTLINE_TASK_TYPE = "ppt_outline_generator"
PPT_OUTLINE_RESOURCE_TYPE = "ppt_outline"


class TeacherPptTaskService:
    """处理教师发起的 PPT 大纲生成任务。"""

    async def generate_outline(
        self,
        *,
        activity_id: int,
        teacher_id: int,
        slide_count: int,
        source_material: str,
    ) -> tuple[AgentTask, LearningResource]:
        """创建任务、调用 PPT Agent 并保存生成资源。"""
        task_id, course_id, activity_title, learning_objective = self._create_task(
            activity_id=activity_id,
            teacher_id=teacher_id,
            slide_count=slide_count,
            source_material=source_material,
        )

        self._mark_task_running(task_id)

        try:
            agent_request = PptOutlineGenerationRequest(
                course_id=course_id,
                activity_id=activity_id,
                activity_title=activity_title,
                learning_objective=learning_objective,
                slide_count=slide_count,
                source_material=source_material,
            )
            agent = teacher_agent_registry.get_ppt_outline_agent()
            result = await agent.generate(agent_request)

            return self._save_generated_outline(
                task_id=task_id,
                activity_id=activity_id,
                teacher_id=teacher_id,
                slides=result.slides,
            )
        except Exception as error:
            self._mark_task_failed(task_id, error)
            logger.exception(
                "teacher_ppt_outline_generation_failed",
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
        slide_count: int,
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
                    detail="Cannot generate PPT for another teacher's activity",
                )

            if activity.status != DRAFT:
                raise HTTPException(
                    status_code=409,
                    detail="PPT can only be generated for a draft activity",
                )

            task = AgentTask(
                task_type=PPT_OUTLINE_TASK_TYPE,
                status=QUEUED,
                creator_id=teacher_id,
                course_id=activity.course_id,
                activity_id=activity.id,
                input_data={
                    "slide_count": slide_count,
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

    def _save_generated_outline(
        self,
        *,
        task_id: int,
        activity_id: int,
        teacher_id: int,
        slides: list[PptOutlineSlide],
    ) -> tuple[AgentTask, LearningResource]:
        """替换活动的旧 PPT 大纲，并保存新生成资源。"""
        with Session(database_service.engine) as session:
            activity = session.get(LearningActivity, activity_id)
            if activity is None or activity.status != DRAFT:
                raise HTTPException(
                    status_code=409,
                    detail="Activity is no longer available for PPT generation",
                )

            course = session.get(Course, activity.course_id)
            if course is None or course.teacher_id != teacher_id:
                raise HTTPException(
                    status_code=403,
                    detail="Teacher permission is no longer valid",
                )

            session.exec(
                delete(LearningResource).where(
                    LearningResource.activity_id == activity_id,
                    LearningResource.resource_type == PPT_OUTLINE_RESOURCE_TYPE,
                )
            )

            resource = LearningResource(
                activity_id=activity_id,
                created_by=teacher_id,
                generated_by_task_id=task_id,
                resource_type=PPT_OUTLINE_RESOURCE_TYPE,
                title=f"{activity.title} - PPT 大纲",
                content_data={
                    "slides": [slide.model_dump() for slide in slides],
                },
            )
            session.add(resource)
            session.flush()

            task = session.get(AgentTask, task_id)
            if task is None:
                raise RuntimeError("Agent task not found")

            task.status = SUCCEEDED
            task.result_data = {
                "resource_id": resource.id,
                "slide_count": len(slides),
            }
            task.finished_at = datetime.now(UTC)

            session.add(task)
            session.commit()

            session.refresh(task)
            session.refresh(resource)

            return task, resource

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


teacher_ppt_task_service = TeacherPptTaskService()