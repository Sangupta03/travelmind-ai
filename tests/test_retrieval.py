from core.retrieval import cosine_similarity, find_similar


def test_identical_vectors_have_similarity_one():
    v = [1.0, 2.0, 3.0]
    assert cosine_similarity(v, v) == 1.0


def test_orthogonal_vectors_have_similarity_zero():
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_opposite_vectors_have_similarity_negative_one():
    assert cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == -1.0


def test_mismatched_lengths_return_zero():
    assert cosine_similarity([1.0, 2.0], [1.0, 2.0, 3.0]) == 0.0


def test_empty_vectors_return_zero():
    assert cosine_similarity([], []) == 0.0
    assert cosine_similarity(None, [1.0]) == 0.0


def test_zero_vector_returns_zero_not_a_division_error():
    assert cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0


def test_find_similar_ranks_by_similarity_descending():
    query = [1.0, 0.0]
    candidates = [
        ("orthogonal", [0.0, 1.0]),
        ("identical", [1.0, 0.0]),
        ("opposite", [-1.0, 0.0]),
    ]
    result = find_similar(query, candidates, top_k=3)
    assert result == ["identical", "orthogonal", "opposite"]


def test_find_similar_respects_top_k():
    query = [1.0, 0.0]
    candidates = [(f"item{i}", [1.0, 0.0]) for i in range(5)]
    result = find_similar(query, candidates, top_k=2)
    assert len(result) == 2


def test_find_similar_skips_missing_embeddings():
    query = [1.0, 0.0]
    candidates = [("has_embedding", [1.0, 0.0]), ("no_embedding", None)]
    result = find_similar(query, candidates, top_k=5)
    assert result == ["has_embedding"]


def test_find_similar_returns_empty_for_missing_query():
    candidates = [("item", [1.0, 0.0])]
    assert find_similar(None, candidates) == []
    assert find_similar([], candidates) == []
