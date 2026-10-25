import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ai.liveness import blink_detected, head_moved, check_liveness

def test_blink():
    assert blink_detected([0.3, 0.1, 0.3]) is True
    assert blink_detected([0.3, 0.3, 0.3]) is False

def test_head_movement():
    assert head_moved([(0, 0), (10, 0)]) is True
    assert head_moved([(0, 0), (1, 0)]) is False

def test_liveness_requires_both_signals():
    assert check_liveness([0.3, 0.1, 0.3], [(0, 0), (10, 0)]).passed is True
    assert check_liveness([0.3, 0.1, 0.3], [(0, 0), (0, 0)]).passed is False
    assert check_liveness([0.3, 0.3], [(0, 0), (0, 0)]).passed is False
