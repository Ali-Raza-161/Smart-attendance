"""Face embedding interface (512 dimensions).

A deep network (ArcFace via InsightFace, or FaceNet) converts an aligned
face crop into a 512-number vector. Model weights are NOT included in
this project and are NOT downloaded here. If no embedding backend is
installed, get_embedding() raises ModelNotAvailable — it never returns
a random or fake embedding as if it were a real face.
"""
from __future__ import annotations
from typing import List

EMBEDDING_DIM = 512

class ModelNotAvailable(Exception):
    """Raised when no face-embedding model backend is available."""

def get_embedding(face_crop_bytes: bytes) -> List[float]:
    """Return a 512-dim embedding for an aligned face crop, or raise
    ModelNotAvailable. Implementations may plug in InsightFace (ArcFace)
    or facenet-pytorch (FaceNet) here; both are lazy imports so the API
    and tests can run without heavy model downloads."""
    try:
        import insightface  # type: ignore  # noqa: F401
    except ImportError:
        pass
    else:
        raise ModelNotAvailable(
            "InsightFace is installed but no model weights are configured. "
            "Download an ArcFace model and wire it in embedder.py before use."
        )
    try:
        import facenet_pytorch  # type: ignore  # noqa: F401
    except ImportError:
        pass
    else:
        raise ModelNotAvailable(
            "facenet-pytorch is installed but no model weights are configured."
        )
    raise ModelNotAvailable(
        "No face-embedding model is available. Install InsightFace (ArcFace) "
        "or facenet-pytorch (FaceNet), download the model weights, and wire "
        "the backend into embedder.py. This demo never returns a fake embedding."
    )

def is_available() -> bool:
    try:
        get_embedding(b"")
    except ModelNotAvailable:
        return False
    except Exception:
        return False
    return True
