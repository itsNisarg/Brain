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
from azure.identity.aio import VisualStudioCodeCredential
from dotenv import load_dotenv
from PIL import Image
from pydantic import BaseModel

from brain.tools.screenshot import take_screenshot


class ScreenAnalysisResponseFormat(BaseModel):
    """The response format of the GoalAgent,
    which includes the goal, assumptions, and constraints.
    """

    screen_caption: str = ""
    screen_description: str = ""
    in_process: bool | None = None
    mouse_at_right_pos: bool | None = None


class ScreenAnalyzerAgent:
    def __init__(
        self,
        prompt_path: str | None = "screen_analyze.md",
        context_providers: list[BaseHistoryProvider | InMemoryHistoryProvider] = [],
        tools: list[FunctionTool] = [],
    ) -> None:

        logger.info("Initializing ScreenAnalyzerAgent...")
        load_dotenv()  # Load environment variables from .env file

        if (
            prompt_path is not None
            and files("brain.prompts").joinpath(prompt_path).is_file()
        ):
            self.prompt = (
                files("brain.prompts").joinpath(prompt_path).read_text(encoding="utf-8")
            )
        else:
            self.prompt = "You are a helpful assistant that analyzes the user's screen and provides a caption, description, and other relevant information in a structured format."

        self._credential = VisualStudioCodeCredential()
        self.agent = AzureOpenAIResponsesClient(
            project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            deployment_name=os.environ["CHAT_AGENT"],
            credential=self._credential,
        ).as_agent(
            name="ScreenAnalyzerAgent",
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
        query: str | None,
        screenshot: bytes | None,
        session: AgentSession | None,
        screen_width: int | None = None,
        screen_height: int | None = None,
        mouse_x: int | None = None,
        mouse_y: int | None = None,
    ) -> ScreenAnalysisResponseFormat:
        
        system_message = Message(
            role="system",
            contents=[
                Content.from_text(
                    text=f"""Screen dimensions: {screen_width}x{screen_height} with top left as (0,0) and bottom right as ({screen_width},{screen_height}).
                    Current Mouse position: ({mouse_x}, {mouse_y}) represented as a red dot insidde a white circle on the screen."""
                ),
            ],
        )

        user_message = Message(
            role="user",
            contents=[
                Content.from_text(text=query if query else "Hi!"),
                Content.from_data(
                    data=screenshot if screenshot else b"", media_type="image/png"
                ),
            ],
        )

        result = await self.agent.run(
            [system_message, user_message],
            stream=True,
            options={"response_format": ScreenAnalysisResponseFormat},
            session=session,
        )

        i = 1
        async for chunk in result:
            if chunk.text:
                logger.info(f"{i} Chunks received: {chunk.text}")
            i += 1

        final_result = await result.get_final_response()

        if structured_data := final_result.value:
            logger.info(f"Structured data extracted.")
            logger.info(f"Screen Caption: {structured_data.screen_caption}")
            logger.info(f"Screen Description: {structured_data.screen_description}")
            logger.info(f"In Process: {structured_data.in_process}")
            logger.info(
                f"Mouse at Right Position: {structured_data.mouse_at_right_pos}"
            )
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

    screen_analyzer_agent = ScreenAnalyzerAgent()
    query = "Create a new task in Microsoft To Do."
    image, image_grid, screen_width, screen_height, mouse_x, mouse_y, filepath = (
        take_screenshot("default_session")
    )
    asyncio.run(
        screen_analyzer_agent.run(
            query=query,
            screenshot=image,
            session=None,
            screen_width=screen_width,
            screen_height=screen_height,
            mouse_x=mouse_x,
            mouse_y=mouse_y,
        )
    )
