import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ai.matcher import cosine_similarity, euclidean_distance, match_embedding, is_duplicate

def test_cosine_identical_is_one():
    assert cosine_similarity([1, 0, 0], [1, 0, 0]) == 1.0

def test_cosine_orthogonal_is_zero():
    assert cosine_similarity([1, 0], [0, 1]) == 0.0

def test_euclidean():
    assert euclidean_distance([0, 0], [3, 4]) == 5.0

def test_match_above_threshold():
    # Synthetic 512-dim-style vectors (random-looking numbers, NOT faces).
    q = [1.0] + [0.0] * 511
    stored = {"alice": [[1.0] + [0.0] * 511], "bob": [[0.0, 1.0] + [0.0] * 510]}
    assert match_embedding(q, stored, threshold=0.5) == ("alice", 1.0)

def test_match_below_threshold_is_unknown():
    q = [1.0] + [0.0] * 511
    stored = {"alice": [[0.0, 1.0] + [0.0] * 510]}
    assert match_embedding(q, stored, threshold=0.5) is None

def test_duplicate_prevention():
    assert is_duplicate("p1", ["p1", "p2"]) is True
    assert is_duplicate("p3", ["p1", "p2"]) is False
