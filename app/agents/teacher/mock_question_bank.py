"""用于验证教师题库 Agent 接入流程的模拟实现。"""

from app.agents.contracts import (
    QuestionBankGenerationRequest,
    QuestionBankGenerationResult,
    QuestionDraft,
)


class MockTeacherQuestionBankAgent:
    """返回固定 Python 条件判断题目的教师题库 Agent。"""

    async def generate(
        self,
        request: QuestionBankGenerationRequest,
    ) -> QuestionBankGenerationResult:
        """生成 Demo 使用的固定题目草稿。"""
        questions = [
            QuestionDraft(
                prompt="下面哪个表达式可以判断整数 n 是否为偶数？",
                options=[
                    "n / 2 == 0",
                    "n % 2 == 0",
                    "n // 2 == 0",
                ],
                correct_option_index=1,
                explanation="取模运算符 % 用于计算余数，偶数除以 2 的余数为 0。",
            ),
            QuestionDraft(
                prompt="当 score 大于等于 60 时，下面哪段代码会输出“及格”？",
                options=[
                    'if score < 60: print("及格")',
                    'if score >= 60: print("及格")',
                    'if score == 60: print("及格")',
                ],
                correct_option_index=1,
                explanation="大于等于使用 >= 运算符。",
            ),
            QuestionDraft(
                prompt="下面哪段代码正确使用了 if/else 结构？",
                options=[
                    'if age >= 18 print("成人") else print("未成年")',
                    'if age >= 18: print("成人") else: print("未成年")',
                    'if age >= 18: print("成人")\nelse: print("未成年")',
                ],
                correct_option_index=2,
                explanation="Python 的 else 必须单独换行，并与 if 保持相同缩进。",
            ),
        ]

        return QuestionBankGenerationResult(
            questions=questions[: request.question_count],
        )
