import asyncio
import os
import warnings

os.environ.setdefault("DEFER_PYDANTIC_BUILD", "false")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")


from agent_framework import Content, Message
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity.aio import VisualStudioCodeCredential
from dotenv import load_dotenv
from pydantic import BaseModel


class GoalResponseFormat(BaseModel):
    """The response format of the GoalAgent,
    which includes the goal, assumptions, and constraints.
    """

    goal: str = ""
    assumptions: str | None = None
    constraints: str | None = None


class GoalAgent:
    def __init__(self, prompt_path: str | None = "prompts/goal_prompt.md", context_provider: GoalContextProvider | None = None):

        load_dotenv()  # Load environment variables from .env file

        if prompt_path is not None and os.path.exists(prompt_path):
            with open("prompts/goal_prompt.md", "r", encoding="utf-8") as f:
                self.prompt = f.read()  # Load the prompt template from an external file
        else:
            self.prompt = "You are a helpful assistant that extracts the user's goal, assumptions, and constraints from their query and provides it in a structured format."

        self._credential = VisualStudioCodeCredential()
        self.agent = AzureOpenAIResponsesClient(
            project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            deployment_name=os.environ["CHAT_AGENT"],
            credential=self._credential,
        ).as_agent(name="GoalAgent", instructions=self.prompt)

    async def run(self, query: str):
        user_message = Message(role="user", contents=[Content.from_text(text=query)])

        result = await self.agent.run(
            user_message, stream=True, options={"response_format": GoalResponseFormat}
        )
        
        async for chunk in result:
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print()  # for newline after streaming output is done

        final_result = await result.get_final_response()

        if structured_data := final_result.value:
            return structured_data
        else:
            print("No structured data found in the response.")
            raise ValueError(
                "Expected structured data in the response, but none was found."
            )


if __name__ == "__main__":
    goal_agent = GoalAgent()
    query = "I want to activate my PIM roles in Azure."
    asyncio.run(goal_agent.run(query))
