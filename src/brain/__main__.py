import asyncio
import logging
import os
from datetime import datetime

from agent_framework import (BaseHistoryProvider, InMemoryHistoryProvider,
                             Message)
from dotenv import load_dotenv
from tinydb import TinyDB

from brain.agents.goal_agent import GoalAgent
from brain.context_history.history_provider import (GlobalAuditProvider,
                                                    GoalContextProvider)
from brain.tools.screenshot import take_screenshot

# Create a logger instance for this module
logger = logging.getLogger(__name__)


async def main(session_name: str) -> None:
    logger.info("Setting up conversation history...")

    audit_db = TinyDB(
        f"./sessions/{session_name}/history.json"
    )  # Create a TinyDB instance for this session

    logger.info("Setting up goal context database...")
    goal_db = TinyDB(f"./learnings/goals/history.json")  # Separate DB for goal context

    logger.info("Setting up screen analysis context database...")
    screen_db = TinyDB(
        f"./learnings/screen_analysis/screen_history.json"
    )  # Separate DB for screen analysis context

    logger.info("Setup complete. Starting agent...")
    logger.info("Hello from brain!")

    logger.info("Initializing context providers...")
    audit = GlobalAuditProvider(db=audit_db)
    goal_context_provider = GoalContextProvider(db=goal_db)
    logger.info("Initialized context providers...")

    goal_agent = GoalAgent(context_providers=[goal_context_provider, audit])
    goal_session = goal_agent.agent.create_session(session_id=f"goal_{session_name}")
    query = "I want to create a task in Microsoft To Do"

    logger.info(f"Running agent with query: {query}")
    result = await goal_agent.run(query, goal_session)
    logger.info(f"Agent run completed.")


def run() -> None:
    """Synchronous entry point for the `brain` CLI command."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_name = f"session_{timestamp}"

    print("Setting up folder structure...")
    os.makedirs("./sessions", exist_ok=True)
    os.makedirs("./learnings", exist_ok=True)
    os.makedirs("./learnings/goals", exist_ok=True)
    os.makedirs("./learnings/screen_analysis", exist_ok=True)
    os.makedirs(f"./sessions/{session_name}", exist_ok=True)
    os.makedirs(f"./sessions/{session_name}/screenshots", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(f"./sessions/{session_name}/brain.log"),
            logging.StreamHandler(),
        ],
    )

    logger.info(f"Session created: {session_name}")

    if not os.path.exists(".env"):
        logger.warning(".env file not found. Please create a .env file with the necessary API keys.")
    else:
        logger.info(".env file found.")

    load_dotenv()
    logger.info("Environment variables loaded. Starting main function...")

    asyncio.run(main(session_name))


if __name__ == "__main__":
    run()
