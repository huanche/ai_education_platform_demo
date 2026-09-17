"""Business logic for courses and enrollments."""

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.services.database import database_service


class CourseService:
    """Manage courses and student enrollments."""

    async def create_course(
        self,
        *,
        teacher_id: int,
        title: str,
        description: str,
    ) -> Course:
        """Create a course owned by a teacher."""
        with Session(database_service.engine) as session:
            course = Course(
                teacher_id=teacher_id,
                title=title,
                description=description,
            )
            session.add(course)
            session.commit()
            session.refresh(course)
            return course

    async def get_courses_by_teacher(self, teacher_id: int) -> list[Course]:
        """Return all courses created by one teacher."""
        with Session(database_service.engine) as session:
            statement = select(Course).where(Course.teacher_id == teacher_id).order_by(Course.created_at.desc())
            return list(session.exec(statement).all())

    async def enroll_student(
        self,
        *,
        course_id: int,
        student_id: int,
    ) -> Enrollment:
        """Enroll a student in an existing course."""
        with Session(database_service.engine) as session:
            course = session.get(Course, course_id)
            if course is None:
                raise HTTPException(status_code=404, detail="Course not found")

            statement = select(Enrollment).where(
                Enrollment.course_id == course_id,
                Enrollment.student_id == student_id,
            )
            existing_enrollment = session.exec(statement).first()
            if existing_enrollment is not None:
                raise HTTPException(status_code=409, detail="Already enrolled in this course")

            enrollment = Enrollment(
                course_id=course_id,
                student_id=student_id,
            )
            session.add(enrollment)
            session.commit()
            session.refresh(enrollment)
            return enrollment

    async def get_courses_for_student(self, student_id: int) -> list[Course]:
        """Return all courses a student has enrolled in."""
        with Session(database_service.engine) as session:
            statement = (
                select(Course)
                .join(Enrollment, Enrollment.course_id == Course.id)
                .where(Enrollment.student_id == student_id)
                .order_by(Course.created_at.desc())
            )
            return list(session.exec(statement).all())


course_service = CourseService()
