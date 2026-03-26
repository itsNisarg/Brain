import importlib.util
import io
import json
import os
import warnings

os.environ.setdefault("DEFER_PYDANTIC_BUILD", "false")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# import aiofiles
from agent_framework import Content, Message
from agent_framework.azure import AzureAIClient, AzureOpenAIResponsesClient
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import VisualStudioCodeCredential
from dotenv import load_dotenv
from PIL import Image

