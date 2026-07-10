import json
import logging
import time
from google.genai import Client, types
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

client = Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"


def _generate_with_retry(prompt: str, config=None, retries=3):
    for attempt in range(retries):
        try:
            return client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=config,
            )
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                wait_time = 45
                logger.warning("Gemini quota hit. Waiting %s seconds before retrying...", wait_time)
                time.sleep(wait_time)
            else:
                raise e
    return None


def call_llm(prompt: str, retries=3):
    response = _generate_with_retry(prompt, retries=retries)
    if response is None:
        return "Error: Gemini API quota exceeded. Please try again later."
    return response.text


def call_llm_json(prompt: str, schema: dict, retries=3):
    """
    Same as call_llm, but forces Gemini to return JSON matching `schema`
    (a JSON Schema dict) instead of coaxing JSON out of free text.
    Returns a parsed dict, or None if the call failed after all retries.
    """
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=schema,
    )
    response = _generate_with_retry(prompt, config=config, retries=retries)
    if response is None:
        return None
    try:
        return json.loads(response.text)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error("Gemini returned invalid JSON despite response_schema: %s", e)
        return None


