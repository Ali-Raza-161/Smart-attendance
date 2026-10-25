"""Face detection interface.

Detects faces and returns bounding boxes + landmarks. OpenCV is optional:
if it is not installed, or no detector backend is available, a clear
DetectorUnavailable error is raised. A blank synthetic image is never
reported as a face.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import io

class DetectorUnavailable(Exception):
    """Raised when no face-detection backend is available."""

@dataclass
class FaceBox:
    x: int
    y: int
    width: int
    height: int
    landmarks: Optional[dict] = None

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "width": self.width,
                "height": self.height, "landmarks": self.landmarks or {}}

def detect_faces(image_bytes: bytes) -> List[FaceBox]:
    """Detect faces in JPEG/PNG bytes. Returns [] if the image is valid
    but contains no face. Raises DetectorUnavailable if OpenCV is missing."""
    try:
        import cv2  # type: ignore
        import numpy as np
    except ImportError as exc:
        raise DetectorUnavailable(
            "OpenCV is not installed. Install opencv-python and a detector "
            "backend (RetinaFace, MTCNN or YuNet) to enable detection."
        ) from exc
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image: expected a valid JPEG or PNG.")
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    cascade = cv2.CascadeClassifier(cascade_path)
    if cascade.empty():
        raise DetectorUnavailable("OpenCV Haar cascade could not be loaded.")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5,
                                     minSize=(30, 30))
    return [FaceBox(int(x), int(y), int(w), int(h)) for (x, y, w, h) in rects]

def decode_image_size(image_bytes: bytes) -> tuple:
    """Return (width, height) of an image without running detection."""
    from PIL import Image
    with Image.open(io.BytesIO(image_bytes)) as im:
        return im.size
