"""学生 Agent 注册与获取入口。"""

from app.agents.contracts import StudentLearningGuideAgent
from app.agents.student.learning_guide_graph import (
    LangGraphStudentLearningGuideAgent,
)


class StudentAgentRegistry:
    """集中管理当前启用的学生 Agent。"""

    def __init__(self) -> None:
        """初始化当前启用的学生 Agent。"""
        self._learning_guide_agent: StudentLearningGuideAgent = (
            LangGraphStudentLearningGuideAgent()
        )

    def get_learning_guide_agent(self) -> StudentLearningGuideAgent:
        """返回当前启用的学生学习引导 Agent。"""
        return self._learning_guide_agent


student_agent_registry = StudentAgentRegistry()