import asyncio
import os
from assistants.goal_agent import GoalAgent

from datetime import datetime

async def main():
    timestamp = datetime.now().isoformat()
    session_name = f"session_{timestamp}"
    print(f"Creating folder: {session_name}")
    os.makedirs(session_name, exist_ok=True)  # Create a folder for this session

    print("Hello from brain!")
    goal_agent = GoalAgent()
    query = "I want to create a task in Microsoft To Do"
    result = await goal_agent.run(query)
    print("Goal:", result.goal)
    print("Assumptions:", result.assumptions)
    print("Constraints:", result.constraints)


if __name__ == "__main__":
    asyncio.run(main())
