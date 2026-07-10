"""
Wraps Gemini's embedding endpoint for the RAG-based trip personalization
feature — turns a short text summary of a trip into a vector so it can
be compared against other trips by semantic similarity.
"""
import logging
import time

from core.llm import client

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "gemini-embedding-001"


def embed_text(text: str, retries: int = 3) -> list:
    """
    Returns a list of floats (the embedding vector), or None if the
    call failed after all retries (e.g. quota exhausted).
    """
    if not text or not text.strip():
        return None

    for attempt in range(retries):
        try:
            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text,
            )
            return response.embeddings[0].values
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                wait_time = 45
                logger.warning("Gemini embedding quota hit. Waiting %s seconds before retrying...", wait_time)
                time.sleep(wait_time)
            else:
                raise e
    return None
