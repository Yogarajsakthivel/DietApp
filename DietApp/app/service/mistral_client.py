# service/mistral_client.py
import os
from mistralai import Mistral
from dotenv import load_dotenv

# Load .env file
load_dotenv()  # loads environment variables from a .env file into os.environ

# Read API key and model from environment
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")

if not MISTRAL_API_KEY:
    raise ValueError("❌ MISTRAL_API_KEY environment variable not set!")

# Initialize Mistral client
client = Mistral(api_key=MISTRAL_API_KEY)

def generate_chat_completion(messages):
    """
    messages: list of dicts, e.g. [{"role": "user", "content": "Hello!"}]
    """
    response = client.chat.complete(
        model=MISTRAL_MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=800
    )
    return response.choices[0].message.content
