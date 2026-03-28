import os
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. "
        "Please set it in your .env file or environment."
    )

client = OpenAI(api_key=api_key)
async_client = AsyncOpenAI(api_key=api_key)