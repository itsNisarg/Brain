import asyncio
import os
import logging
from assistants.goal_agent import GoalAgent
from agent_framework import BaseHistoryProvider, Message, InMemoryHistoryProvider

from datetime import datetime
from tinydb import TinyDB

from context_history.history_provider import GoalContextProvider, GlobalAuditProvider



# Create a logger instance for this module
logger = logging.getLogger(__name__)


async def main():

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_name = f"./interactions/sessions/session_{timestamp}"
    print(f"Creating folder: {session_name}")
    os.makedirs(session_name, exist_ok=True)  # Create a folder for this session

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(f"{session_name}/brain.log"),
            logging.StreamHandler()
        ]
    )

    audit_db = TinyDB(f"{session_name}/history.json")  # Create a TinyDB instance for this session
    goal_db = TinyDB(f"./interactions/goals/history.json")  # Separate DB for goal context

    logger.info(f"Session folder created: {session_name}")
    logger.info("Hello from brain!")
    print("Hello from brain!")

    logger.info("Initializing context providers...")
    audit = GlobalAuditProvider(db=audit_db)
    goal_context_provider = GoalContextProvider(db=goal_db)
    logger.info("Initialized context providers...")

    goal_agent = GoalAgent(context_providers=[goal_context_provider, audit])
    goal_session = goal_agent.agent.create_session(session_id="goal_session")
    query = "I want to create a task in Microsoft To Do"

    logger.info(f"Running agent with query: {query}")
    result = await goal_agent.run(query, goal_session)
    logger.info(f"Agent run completed.")
    

if __name__ == "__main__":
    asyncio.run(main())
