import time
from google.genai import Client
from config import GEMINI_API_KEY

client = Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"

def call_llm(prompt: str, retries=3):
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            return response.text

        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                wait_time = 45
                print(f"\n⚠️ Gemini quota hit. Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                raise e

    return "Error: Gemini API quota exceeded. Please try again later."


