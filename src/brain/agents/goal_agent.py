import asyncio
import logging
import os
import warnings
from importlib.resources import files

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
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity.aio import VisualStudioCodeCredential
from dotenv import load_dotenv
from pydantic import BaseModel


class GoalResponseFormat(BaseModel):
    """The response format of the GoalAgent,
    which includes the goal, assumptions, and constraints.
    """

    goal: str = ""
    assumptions: str = ""
    constraints: str = ""


class GoalAgent:

    def __init__(
        self,
        prompt_path: str | None = "goal_prompt.md",
        context_providers: list[BaseHistoryProvider | InMemoryHistoryProvider] = [],
        tools: list[FunctionTool] = [],
    ) -> None:

        logger.info("Initializing GoalAgent...")

        if (
            prompt_path is not None
            and files("brain.prompts").joinpath(prompt_path).is_file()
        ):
            self.prompt = (
                files("brain.prompts").joinpath(prompt_path).read_text(encoding="utf-8")
            )  # Load the prompt template from an external file
        else:
            self.prompt = "You are a helpful assistant that extracts the user's goal, assumptions, and constraints from their query and provides it in a structured format."

        self._credential = VisualStudioCodeCredential()
        self.agent = AzureOpenAIResponsesClient(
            project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            deployment_name=os.environ["CHAT_AGENT"],
            credential=self._credential,
        ).as_agent(
            name="GoalAgent",
            instructions=self.prompt,
            context_providers=context_providers,
            tools=tools,
        )

        logger.info("GoalAgent initialized.")

    async def __aenter__(self):
        await self.agent.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.agent.__aexit__(*args)

    async def create_session(self, session_id: str) -> AgentSession:
        """Creates a new agent session with the given name."""
        return self.agent.create_session(session_id=session_id)

    async def run(
        self, query: str | None, session: AgentSession | None
    ) -> GoalResponseFormat:

        user_message = Message(
            role="user", contents=[Content.from_text(text=query if query else "Hi!")]
        )

        result = await self.agent.run(
            user_message,
            stream=True,
            options={"response_format": GoalResponseFormat},
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


if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file

    goal_agent = GoalAgent()
    query = "I want to activate my PIM roles in Azure."
    asyncio.run(goal_agent.run(query, session=None))
