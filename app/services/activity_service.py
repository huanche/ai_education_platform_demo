"""Business logic for learning activities."""

from datetime import UTC, datetime

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.activity_status import DRAFT, PUBLISHED
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.learning_activity import LearningActivity
from app.services.database import database_service


class ActivityService:
    """Manage learning activity drafts and publication."""

    async def create_activity(
        self,
        *,
        course_id: int,
        teacher_id: int,
        title: str,
        description: str,
        learning_objective: str,
    ) -> LearningActivity:
        """Create an activity draft for a teacher-owned course."""
        with Session(database_service.engine) as session:
            course = session.get(Course, course_id)
            if course is None:
                raise HTTPException(status_code=404, detail="Course not found")

            if course.teacher_id != teacher_id:
                raise HTTPException(status_code=403, detail="Cannot modify another teacher's course")

            activity = LearningActivity(
                course_id=course_id,
                title=title,
                description=description,
                learning_objective=learning_objective,
                status=DRAFT,
            )
            session.add(activity)
            session.commit()
            session.refresh(activity)
            return activity

    async def get_teacher_activities(
        self,
        *,
        course_id: int,
        teacher_id: int,
    ) -> list[LearningActivity]:
        """Return all activities in a teacher-owned course."""
        with Session(database_service.engine) as session:
            course = session.get(Course, course_id)
            if course is None:
                raise HTTPException(status_code=404, detail="Course not found")

            if course.teacher_id != teacher_id:
                raise HTTPException(status_code=403, detail="Cannot view another teacher's course")

            statement = (
                select(LearningActivity)
                .where(LearningActivity.course_id == course_id)
                .order_by(LearningActivity.created_at.desc())
            )
            return list(session.exec(statement).all())

    async def publish_activity(
        self,
        *,
        activity_id: int,
        teacher_id: int,
    ) -> LearningActivity:
        """Publish an activity owned by the current teacher."""
        with Session(database_service.engine) as session:
            activity = session.get(LearningActivity, activity_id)
            if activity is None:
                raise HTTPException(status_code=404, detail="Activity not found")

            course = session.get(Course, activity.course_id)
            if course is None or course.teacher_id != teacher_id:
                raise HTTPException(status_code=403, detail="Cannot publish another teacher's activity")

            if activity.status == PUBLISHED:
                raise HTTPException(status_code=409, detail="Activity is already published")

            activity.status = PUBLISHED
            activity.published_at = datetime.now(UTC)
            session.add(activity)
            session.commit()
            session.refresh(activity)
            return activity

    async def get_published_activity_for_student(
        self,
        *,
        activity_id: int,
        student_id: int,
    ) -> LearningActivity:
        """Return a published activity only to an enrolled student."""
        with Session(database_service.engine) as session:
            activity = session.get(LearningActivity, activity_id)
            if activity is None or activity.status != PUBLISHED:
                raise HTTPException(status_code=404, detail="Published activity not found")

            statement = select(Enrollment).where(
                Enrollment.course_id == activity.course_id,
                Enrollment.student_id == student_id,
            )
            if session.exec(statement).first() is None:
                raise HTTPException(status_code=403, detail="Not enrolled in this course")

            return activity


activity_service = ActivityService()
