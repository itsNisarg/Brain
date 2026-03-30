import asyncio
import logging
import os
from datetime import datetime
from email.mime import image

from dotenv import load_dotenv
from tinydb import TinyDB

from brain.agents import GoalAgent, GUIActionAgent, ScreenAnalysisAgent
from brain.context_history import (GlobalAuditProvider, GoalContextProvider,
                                   GUIActionAgentContextProvider,
                                   ScreenAnalysisContextProvider)
from brain.tools import (double_click, drag_and_drop, left_click,
                         mouse_position, move_hover, pause_keyboard,
                         pause_mouse, press, right_click, scroll_down,
                         scroll_up, shortcut, take_screenshot, typeset,
                         typetext)

# Create a logger instance for this module
logger = logging.getLogger(__name__)


async def main(session_name: str) -> None:

    # HISTORY SETUP
    # Audit DB
    logger.info("Setting up conversation history...")
    audit_db = TinyDB(
        f"./sessions/{session_name}/history.json"
    )  # Create a TinyDB instance for this session

    # Goal Context DB
    logger.info("Setting up goal context database...")
    goal_db = TinyDB(f"./learnings/goals/history.json")  # Separate DB for goal context

    # Screen Analysis Context DB
    logger.info("Setting up screen analysis context database...")
    screen_db = TinyDB(
        f"./learnings/screen_analysis/screen_history.json"
    )  # Separate DB for screen analysis context

    # GUI Action Context DB
    logger.info("Setting up GUI action context database...")
    gui_action_db = TinyDB(
        f"./learnings/gui_action/gui_action_history.json"
    )  # Separate DB for GUI action context

    logger.info("Setup complete. Starting agent...")

    #####################################################################################

    logger.info("Hello from brain!")

    logger.info("Initializing context providers...")

    # CONTEXT PROVIDERS
    # Audit Context Provider
    audit = GlobalAuditProvider(db=audit_db)

    # Goal Context Provider
    goal_context_provider = GoalContextProvider(db=goal_db)

    # Screen Analysis Context Provider
    screen_context_provider = ScreenAnalysisContextProvider(db=screen_db)

    # GUI Action Context Provider
    gui_action_context_provider = GUIActionAgentContextProvider(db=gui_action_db)

    logger.info("Initialized context providers...")

    #####################################################################################

    # Goal Agent
    goal_agent = GoalAgent(context_providers=[goal_context_provider, audit])
    goal_session = await goal_agent.create_session(session_id=f"goal_{session_name}")
    query = "I want to create a task in Microsoft To Do"  # TODO: replace with user input in the future

    logger.info(f"Running goal agent with query: {query}")
    goal_result = await goal_agent.run(query, goal_session)
    logger.info(f"Goal agent result: {goal_result}")

    ####################################################################################

    # Screen Analysis Agent
    screen_analysis_agent = ScreenAnalysisAgent(
        context_providers=[screen_context_provider, audit], tools=[]
    )
    screen_analysis_session = await screen_analysis_agent.create_session(
        session_id=f"screen_analysis_{session_name}"
    )

    (
        screenshot,
        screenshot_grid,
        screen_width,
        screen_height,
        mouse_x,
        mouse_y,
        filepath,
    ) = take_screenshot(session_name)

    logger.info("Running screen analysis agent...")
    screen_analysis_result = await screen_analysis_agent.run(
        query=goal_result.goal,
        screenshot=screenshot,
        session=screen_analysis_session,
        screen_width=screen_width,
        screen_height=screen_height,
        mouse_x=mouse_x,
        mouse_y=mouse_y,
    )
    logger.info(f"Screen analysis result: {screen_analysis_result}")

    ####################################################################################

    # GUI Action Agent
    gui_action_agent = GUIActionAgent(
        context_providers=[gui_action_context_provider, audit],
        tools=[
            double_click,
            drag_and_drop,
            move_hover,
            left_click,
            mouse_position,
            pause_keyboard,
            pause_mouse,
            press,
            right_click,
            scroll_down,
            scroll_up,
            shortcut,
            typetext,
        ],
    )
    gui_action_session = await gui_action_agent.create_session(
        session_id=f"gui_action_{session_name}"
    )

    logger.info("Running GUI action agent...")

    gui_action_result = await gui_action_agent.run(
        screenshot=screenshot,
        screenshot_grid=screenshot_grid,
        screen_description=f"{screen_analysis_result.screen_caption}\n{screen_analysis_result.screen_description}",
        goal=goal_result.goal,
        assumptions=goal_result.assumptions,
        constraints=goal_result.constraints,
        session=gui_action_session,
        screen_width=screen_width,
        screen_height=screen_height,
        mouse_x=mouse_x,
        mouse_y=mouse_y,
        process_running=(
            screen_analysis_result.in_process
            if screen_analysis_result.in_process is not None
            else False
        ),
        mouse_in_right_position=(
            screen_analysis_result.mouse_at_right_pos
            if screen_analysis_result.mouse_at_right_pos is not None
            else False
        ),
    )

    logger.info(f"GUI action agent result: {gui_action_result}")

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
        logger.warning(
            ".env file not found. Please create a .env file with the necessary API keys."
        )
    else:
        logger.info(".env file found.")

    load_dotenv()
    logger.info("Environment variables loaded. Starting main function...")

    asyncio.run(main(session_name))


if __name__ == "__main__":
    run()
