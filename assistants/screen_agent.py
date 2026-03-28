import importlib.util
import io
import json
import logging
import os
import warnings

os.environ.setdefault("DEFER_PYDANTIC_BUILD", "false")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# Create a logger instance for this module
logger = logging.getLogger(__name__)

from agent_framework import (
    AgentSession,
    BaseHistoryProvider,
    Content,
    InMemoryHistoryProvider,
    Message,
)
from agent_framework.azure import AzureAIClient, AzureOpenAIResponsesClient
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import VisualStudioCodeCredential
from dotenv import load_dotenv
from PIL import Image
from pydantic import BaseModel


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
        prompt_path: str | None = "prompts/screen_analyze.md",
        context_providers: list[BaseHistoryProvider | InMemoryHistoryProvider] = [],
    ) -> None:

        logger.info("Initializing GoalAgent...")
        load_dotenv()  # Load environment variables from .env file

        if prompt_path is not None and os.path.exists(prompt_path):
            with open("prompts/goal_prompt.md", "r", encoding="utf-8") as f:
                self.prompt = f.read()  # Load the prompt template from an external file
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
        self, query: str | None, screenshot: Image.Image , session: AgentSession | None
    ) -> ScreenAnalysisResponseFormat:
        
        user_message = Message(
            role="user", contents=[Content.from_text(text=query if query else "Hi!")]
        )

        result = await self.agent.run(
            user_message,
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
            return structured_data
        else:
            logger.warning("No structured data found in the response.")
            raise ValueError(
                "Expected structured data in the response, but none was found."
            )
