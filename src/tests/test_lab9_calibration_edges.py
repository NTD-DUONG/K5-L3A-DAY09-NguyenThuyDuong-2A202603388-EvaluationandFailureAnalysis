"""Calibration must not silently accept malformed labels or invalid estimates."""
import pytest
from lab9 import stats

pytestmark = pytest.mark.student


@pytest.mark.parametrize("human,judge", [([], []), (["PASS"], []), (["FAIL"], ["UNKNOWN"])])
def test_invalid_labels_are_rejected(human, judge):
    with pytest.raises(ValueError):
        stats.confusion(human, judge)


def test_no_positive_prediction_or_label_has_zero_precision_recall():
    assert stats.precision_recall(["PASS"], ["PASS"]) == (0.0, 0.0)


@pytest.mark.parametrize("args", [(0.2, 0.5, 0.5), (0.2, 0.1, 0.2),
                                     (float("nan"), 0.8, 0.9), (1.1, 0.8, 0.9)])
def test_unidentifiable_or_invalid_correction_is_rejected(args):
    with pytest.raises(ValueError):
        stats.rogan_gladen(*args)


def test_correction_clips_upper_boundary():
    assert stats.rogan_gladen(1.0, 0.8, 0.9) == 1.0


def test_helpful_judge_is_rejected_despite_perfect_precision():
    from pathlib import Path
    from lab9.judge import calibrate
    result = calibrate(Path("data/eval/judge_helpful_public.csv"))
    assert result["precision"] == 1.0
    assert result["recall"] == 0.3
    assert not result["passed"]
