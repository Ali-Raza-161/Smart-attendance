"""Face matching: cosine similarity / Euclidean distance on 512-dim vectors.

Pure Python (no NumPy required) so matcher tests run anywhere, including
on synthetic vectors. A match is accepted only when the best score is
above the threshold; otherwise the face is 'unknown'. One attendance
record per person per session is enforced by the API layer (see
api/routers/sessions.py), and duplicate checks here help it.
"""
from __future__ import annotations
import math
from typing import Dict, List, Optional, Tuple

DEFAULT_THRESHOLD = 0.5  # cosine similarity, tuned on test data

def _norm(v: List[float]) -> float:
    return math.sqrt(sum(x * x for x in v))

def cosine_similarity(a: List[float], b: List[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Embeddings must have the same dimension.")
    na, nb = _norm(a), _norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)

def euclidean_distance(a: List[float], b: List[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Embeddings must have the same dimension.")
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

def match_embedding(query: List[float], stored: Dict[str, List[List[float]]],
                    threshold: float = DEFAULT_THRESHOLD) -> Optional[Tuple[str, float]]:
    """Best-match person id + score, or None if below threshold / no data.

    `stored` maps person_id -> list of enrolled embeddings (5-10 per person).
    The best score across all of a person's embeddings is used.
    """
    best_id, best_score = None, -1.0
    for person_id, embeddings in stored.items():
        for emb in embeddings:
            score = cosine_similarity(query, emb)
            if score > best_score:
                best_id, best_score = person_id, score
    if best_id is None or best_score < threshold:
        return None
    return best_id, best_score

def is_duplicate(person_id: str, already_marked: List[str]) -> bool:
    """True if this person already has an attendance record this session."""
    return person_id in already_marked
