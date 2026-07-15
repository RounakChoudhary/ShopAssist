import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
import redis.asyncio as redis

load_dotenv()

# API Keys & Strings

LLM_API_KEY = os.getenv("OPENAI_API_KEY")
if not LLM_API_KEY:
    print("[DEV ERROR] Setup Failed: OPENAI_API_KEY missing in environment variables.")
    raise RuntimeError("OPENAI_API_KEY is not set.")

# Global Clients

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Initialize the client with the API key

client = AsyncOpenAI(
    api_key=LLM_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# hardcoded greetings

GREETING_RESPONSES = [
    "Hello! How can I assist you with your shopping today?",
    "Hi there! Looking for something special?",
    "Greetings! What can I help you find today?",
    "Hey! Ready to explore some great products?",
    "Good day! How can I make your shopping experience better?"
]