"""教师 Agent 注册与获取入口。"""

from app.agents.contracts import (
    TeacherPptOutlineAgent,
    TeacherQuestionBankAgent,
)
from app.agents.teacher.ppt_outline_graph import LangGraphTeacherPptOutlineAgent
from app.agents.teacher.question_graph import LangGraphTeacherQuestionBankAgent


class TeacherAgentRegistry:
    """集中管理当前启用的教师 Agent。"""

    def __init__(self) -> None:
        """初始化当前启用的教师 Agent。"""
        self._question_bank_agent: TeacherQuestionBankAgent = (
            LangGraphTeacherQuestionBankAgent()
        )
        self._ppt_outline_agent: TeacherPptOutlineAgent = (
            LangGraphTeacherPptOutlineAgent()
        )

    def get_question_bank_agent(self) -> TeacherQuestionBankAgent:
        """返回当前启用的题库 Agent。"""
        return self._question_bank_agent

    def get_ppt_outline_agent(self) -> TeacherPptOutlineAgent:
        """返回当前启用的 PPT 大纲 Agent。"""
        return self._ppt_outline_agent


teacher_agent_registry = TeacherAgentRegistry()