# Copyright (c) Microsoft. All rights reserved.

import os
import warnings

os.environ.setdefault("DEFER_PYDANTIC_BUILD", "false")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

import asyncio
import importlib.util
import io
import json
import uuid

# import aiofiles
import yaml
from agent_framework import Content, Message
from agent_framework.azure import AzureAIClient, AzureOpenAIResponsesClient
from agent_framework.mem0 import Mem0ContextProvider
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import VisualStudioCodeCredential
from dotenv import load_dotenv
from PIL import Image
from pydantic import BaseModel

credential = VisualStudioCodeCredential()

"""
OpenAI Responses Client with Structured Output Example

This sample demonstrates using structured output capabilities with OpenAI Responses Client,
showing Pydantic model integration for type-safe response parsing and data extraction.
"""


async def example_multiple_agents() -> None:
    """Example 3: Multiple agents with different thread configurations."""
    print("3. Multiple Agents with Different Thread Configurations:")
    print("-" * 40)

    agent_id_1 = "agent_personal"
    agent_id_2 = "agent_work"

    credential = VisualStudioCodeCredential()

    personal_agent = AzureOpenAIResponsesClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        deployment_name=os.environ["CHAT_AGENT"],
        credential=credential,
    ).as_agent(name="PersonalAgent", instructions="You are a personal assistant that helps with personal tasks.",
               context_providers=[
                Mem0ContextProvider(
                    source_id="mem0",
                    agent_id=agent_id_1,
                )
            ])

    work_agent = AzureOpenAIResponsesClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        deployment_name=os.environ["CHAT_AGENT"],
        credential=credential,
    ).as_agent(name="WorkAgent", instructions="You are a work assistant that helps with professional tasks.",
               context_providers=[
                Mem0ContextProvider(
                    source_id="mem0",
                    agent_id=agent_id_1,
                )
            ])

    # Store personal information
    query = (
        "Remember that I like to exercise at 6 AM and prefer outdoor activities."
    )
    print(f"User to Personal Agent: {query}")
    result = await personal_agent.run(query)
    print(f"Personal Agent: {result}\n")

    # Store work information
    query = "Remember that I have team meetings every Tuesday at 2 PM."
    print(f"User to Work Agent: {query}")
    result = await work_agent.run(query)
    print(f"Work Agent: {result}\n")

    # Test memory isolation
    query = "What do you know about my schedule?"
    print(f"User to Personal Agent: {query}")
    result = await personal_agent.run(query)
    print(f"Personal Agent: {result}\n")

    print(f"User to Work Agent: {query}")
    result = await work_agent.run(query)
    print(f"Work Agent: {result}\n")


async def main() -> None:
    load_dotenv()  # Load environment variables from .env file
    print("=== Mem0 Thread Management Example ===\n")

    await example_multiple_agents()


if __name__ == "__main__":
    asyncio.run(main())
