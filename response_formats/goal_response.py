"""The GoalResponse class defines the output of the GoalAgent,
which includes the goal, assumptions, and constraints.
"""

from pydantic import BaseModel


class GoalResponse(BaseModel):
    """The response format of the GoalAgent,
    which includes the goal, assumptions, and constraints.
    """

    goal: str = ""
    assumptions: str | None = None
    constraints: str | None = None
