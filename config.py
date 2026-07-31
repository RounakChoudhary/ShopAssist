import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
import redis.asyncio as redis
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


def get_project_path(env_name: str, default: str) -> Path:
    path = Path(os.getenv(env_name, default))
    return path if path.is_absolute() else BASE_DIR / path


POLICY_FOLDER = get_project_path(
    "POLICY_FOLDER",
    "data/policies",
)

CHROMA_DB_PATH = get_project_path(
    "CHROMA_DB_PATH",
    "chroma_data",
)

CHROMA_COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION_NAME",
    "shopassist_policies",
)


# API Keys & Strings

LLM_API_KEY = os.getenv("OPENAI_API_KEY")
if not LLM_API_KEY:
    print("[DEV ERROR] Setup Failed: OPENAI_API_KEY missing in environment variables.")
    raise RuntimeError("OPENAI_API_KEY is not set.")

# Global Clients

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Initialize the client with the API key

client = AsyncOpenAI(api_key=LLM_API_KEY, base_url="https://api.groq.com/openai/v1")
# Embedding Model
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# hardcoded greetings

GREETING_RESPONSES = [
    "Hello! How can I assist you with your shopping today?",
    "Hi there! Looking for something special?",
    "Greetings! What can I help you find today?",
    "Hey! Ready to explore some great products?",
    "Good day! How can I make your shopping experience better?",
]
