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


def trip_summary_text(destination: str, user_input: str) -> str:
    """
    Builds the text that gets embedded for a trip — used identically for
    a new trip's retrieval query and for every stored past trip, so both
    sides of the similarity comparison are embedded the same way.
    """
    destination = (destination or "").strip()
    user_input = (user_input or "").strip()
    return f"Trip to {destination}: {user_input}".strip()


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
