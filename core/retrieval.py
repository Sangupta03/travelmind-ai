"""
Cosine similarity + top-k ranking for retrieving semantically similar
past trips, given embedding vectors. Pure functions, no I/O — the
embedding calls themselves live in core/embeddings.py.

Plain Python (no numpy) is intentional: at the scale of one user's trip
history (dozens of rows, not millions), a linear scan is simpler to
reason about and fast enough — a vector DB would be infrastructure the
data volume doesn't justify.
"""
import math


def cosine_similarity(a: list, b: list) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def find_similar(query_embedding: list, candidates: list, top_k: int = 3) -> list:
    """
    candidates: list of (item, embedding) pairs.
    Returns the top_k items (not the embeddings), sorted by similarity
    descending. Candidates with a missing/None embedding are skipped.
    """
    if not query_embedding:
        return []

    scored = []
    for item, embedding in candidates:
        if not embedding:
            continue
        score = cosine_similarity(query_embedding, embedding)
        scored.append((score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:top_k]]
