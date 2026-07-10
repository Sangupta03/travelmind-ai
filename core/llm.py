import logging
import time
from google.genai import Client
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

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
                logger.warning("Gemini quota hit. Waiting %s seconds before retrying...", wait_time)
                time.sleep(wait_time)
            else:
                raise e

    return "Error: Gemini API quota exceeded. Please try again later."


