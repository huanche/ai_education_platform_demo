"""Database model imports for metadata registration."""

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.thread import Thread
from app.models.learning_activity import LearningActivity
from app.models.question import Question
from app.models.submission import Submission

from app.models.agent_task import AgentTask
from app.models.learning_resource import LearningResource

__all__ = [
    "Course",
    "Enrollment",
    "LearningActivity",
    "Question",
    "Submission",
    "Thread",
    "AgentTask",
    "LearningResource",
]
