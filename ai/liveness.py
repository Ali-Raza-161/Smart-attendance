"""Liveness / anti-spoofing check interface.

Simple, honest checks: eye blinks (eye-aspect-ratio dip then recovery)
and small head movement between frames. These reduce spoofing with a
printed photo or a still phone screen, but they CANNOT stop advanced
spoofing (video replay, masks, deepfakes). Depth / infrared cameras are
listed as future work in the README. No check here ever claims a face
is 'definitely live' — it returns a score and a pass/fail against a
configurable threshold.
"""
from __future__ import annotations
from typing import List

class LivenessResult:
    def __init__(self, passed: bool, score: float, reason: str):
        self.passed = passed
        self.score = score
        self.reason = reason

    def to_dict(self) -> dict:
        return {"passed": self.passed, "score": self.score, "reason": self.reason}

def blink_detected(eye_aspect_ratios: List[float], blink_threshold: float = 0.2) -> bool:
    """A blink is an EAR dip below threshold followed by a recovery above it."""
    dipped = False
    for ear in eye_aspect_ratios:
        if ear < blink_threshold:
            dipped = True
        elif dipped and ear >= blink_threshold:
            return True
    return False

def head_moved(landmark_positions: List[tuple], min_movement: float = 5.0) -> bool:
    """True if the nose/face centre moved at least min_movement pixels
    between the first and last frame."""
    if len(landmark_positions) < 2:
        return False
    (x1, y1), (x2, y2) = landmark_positions[0], landmark_positions[-1]
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 >= min_movement

def check_liveness(eye_aspect_ratios: List[float],
                   landmark_positions: List[tuple]) -> LivenessResult:
    blink = blink_detected(eye_aspect_ratios)
    moved = head_moved(landmark_positions)
    score = (0.6 if blink else 0.0) + (0.4 if moved else 0.0)
    if blink and moved:
        return LivenessResult(True, score, "Blink and head movement detected.")
    if blink or moved:
        return LivenessResult(False, score,
            "Only one liveness signal detected; require both blink and movement.")
    return LivenessResult(False, 0.0,
        "No blink or head movement detected; possible photo/screen spoof.")
