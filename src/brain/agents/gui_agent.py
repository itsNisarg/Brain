import asyncio
import logging
import os
import warnings
from importlib.resources import files

from dotenv import load_dotenv

os.environ.setdefault("DEFER_PYDANTIC_BUILD", "false")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# Create a logger instance for this module
logger = logging.getLogger(__name__)

from agent_framework import (
    AgentSession,
    BaseHistoryProvider,
    Content,
    FunctionTool,
    InMemoryHistoryProvider,
    Message,
)
from agent_framework.azure import AzureAIClient, AzureOpenAIResponsesClient
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import VisualStudioCodeCredential, ManagedIdentityCredential, AzureCliCredential
from dotenv import load_dotenv
from PIL import Image
from pydantic import BaseModel

from brain.tools import (
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
    take_screenshot,
    typeset,
    typetext,
)


class GUIActionAgentResponseFormat(BaseModel):
    """The response format of the GoalAgent,
    which includes the goal, assumptions, and constraints.
    """

    action_taken: str = ""
    tool_called: str = ""
    screen_analysis_goal: str = ""
    goal_achieved: bool = False


class GUIActionAgent:
    def __init__(
        self,
        prompt_path: str | None = "gui_prompt.md",
        context_providers: list[BaseHistoryProvider | InMemoryHistoryProvider] = [],
        tools: list[FunctionTool] = [],
        cred: VisualStudioCodeCredential | ManagedIdentityCredential | AzureCliCredential | None = None,
    ) -> None:

        logger.info("Initializing GUIActionAgent...")

        if (
            prompt_path is not None
            and files("brain.prompts").joinpath(prompt_path).is_file()
        ):
            self.prompt = (
                files("brain.prompts").joinpath(prompt_path).read_text(encoding="utf-8")
            )
        else:
            self.prompt = "You are a helpful assistant that performs responsible GUI actions based on the user's instructions."

        self._credential = cred
        self.agent = AzureOpenAIResponsesClient(
            project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            deployment_name=os.environ["REASONING_AGENT"],
            credential=self._credential,
        ).as_agent(
            name="GUIActionAgent",
            instructions=self.prompt,
            context_providers=context_providers,
            tools=tools,
        )

    async def __aenter__(self):
        await self.agent.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.agent.__aexit__(*args)

    async def create_session(self, session_id: str) -> AgentSession:
        """Creates a new agent session with the given name."""
        return self.agent.create_session(session_id=session_id)

    async def run(
        self,
        screenshot: bytes | None,
        screenshot_grid: bytes | None,
        screen_description: str | None,
        goal: str | None,
        assumptions: str | None,
        constraints: str | None,
        session: AgentSession | None,
        screen_width: int | None = None,
        screen_height: int | None = None,
        mouse_x: int | None = None,
        mouse_y: int | None = None,
        process_running: bool = False,
        mouse_in_right_position: bool = False,
    ) -> GUIActionAgentResponseFormat:

        system_message = Message(
            role="system",
            contents=[
                Content.from_text(
                    text=f"""Screen dimensions: {screen_width}x{screen_height} with top left as (0,0) and bottom right as ({screen_width},{screen_height}).
                    Current Mouse position: ({mouse_x}, {mouse_y}) represented as a red dot inside a white circle on the screen.
                    Characters available for typing text: 
                    {typeset}"""
                ),
            ],
        )

        user_message = Message(
            role="user",
            contents=[
                Content.from_text(text=f"Goal:\n{goal}" if goal else "Hi!"),
                Content.from_text(text=f"Assumptions:\n{assumptions}" if assumptions else ""),
                Content.from_text(text=f"Constraints:\n{constraints}" if constraints else ""),
                Content.from_data(
                    data=screenshot if screenshot else b"", media_type="image/png"
                ),
                Content.from_data(
                    data=screenshot_grid if screenshot_grid else b"",
                    media_type="image/png",
                ),
                Content.from_text(
                    text=f"Screen Description: {screen_description}" if screen_description else ""
                ),
                Content.from_text(
                    text=f"There is {'a' if process_running else 'no'} process running as of now."
                ),
                Content.from_text(
                    text=f"The mouse is {'in the right position' if mouse_in_right_position else 'not in the right position'}."
                ),
            ],
        )

        result = await self.agent.run(
            [system_message, user_message],
            stream=True,
            options={"response_format": GUIActionAgentResponseFormat},
            session=session,
            additional_options={"reasoning": {"effort": "high", "summary": "concise"}},
        )

        # i = 1
        # async for chunk in result:
        #     if chunk.text:
        #         logger.info(f"{i} Chunks received: {chunk.text}")
        #     i += 1

        final_result = await result.get_final_response()

        if structured_data := final_result.value:
            logger.info(f"Structured data extracted.")
            logger.info(f"Action taken: {structured_data.action_taken}")
            logger.info(f"Tool called: {structured_data.tool_called}")
            logger.info(f"Screen analysis goal: {structured_data.screen_analysis_goal}")
            logger.info(f"Goal achieved: {structured_data.goal_achieved}")
            return structured_data
        else:
            logger.warning("No structured data found in the response.")
            raise ValueError(
                "Expected structured data in the response, but none was found."
            )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(f"./sessions/default_session/brain.log"),
            logging.StreamHandler(),
        ],
    )

    load_dotenv()  # Load environment variables from .env file
    cred = VisualStudioCodeCredential()
    gui_action_agent = GUIActionAgent(
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
        cred = cred
    )
    goal = "Create a new task in Microsoft To Do."
    image, image_grid, screen_width, screen_height, mouse_x, mouse_y, filepath = (
        take_screenshot("default_session")
    )
    asyncio.run(
        gui_action_agent.run(
            screenshot=image,
            screenshot_grid=image_grid,
            screen_description="The screen shows the current screen with Microsoft To Do app in the taskbar.",
            goal=goal,
            assumptions="The user has access to Microsoft To Do via the app or web, is signed into a Microsoft account, and has permission to create tasks in at least one task list. The user will provide or select task details such as title, due date, and list if needed.",
            constraints="A task cannot be created without at least a task title and an accessible list. Internet access and a valid Microsoft account session may be required depending on the platform being used.",
            session=None,
            screen_width=screen_width,
            screen_height=screen_height,
            mouse_x=mouse_x,
            mouse_y=mouse_y,
            process_running=False,  # Example value
            mouse_in_right_position=False,  # Example value
        )
    )
