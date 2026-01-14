from google.genai import Client
from config import GEMINI_API_KEY

client = Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-2.5-flash"

def call_llm(prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text


