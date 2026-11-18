"""Adversarial report mutations must fail even on an otherwise green run."""
import copy
import pytest
from test_lab9_advanced import ROWS, SPEC, _report

pytestmark = pytest.mark.student


@pytest.mark.parametrize("mutation", ["duplicate", "error", "relabel", "missing", "nan", "summary"])
def test_advanced_green_report_tampering(mutation):
    from lab9.gate import integrity_check
    base = _report(copy.deepcopy(ROWS), {"pass_rate": 1.0})
    pr = copy.deepcopy(base)
    if mutation == "duplicate":
        pr["rows"][-1] = copy.deepcopy(pr["rows"][0])
    elif mutation == "error":
        pr["evaluator_failures"] = ["grader failed on green report"]
    elif mutation == "relabel":
        for row in pr["rows"]:
            row["slices"] = []
    elif mutation == "missing":
        del pr["rows"][0]["pass_rate"]
    elif mutation == "nan":
        pr["rows"][0]["pass_rate"] = float("nan")
    else:
        pr["rows"][0]["pass_rate"] = False
    assert integrity_check(pr, base, SPEC)


def test_advanced_slice_ratchet_cannot_remove_paired_check():
    from lab9.gate import integrity_check
    base = _report(copy.deepcopy(ROWS), {"pass_rate": 1.0})
    spec = dict(SPEC, slices=[dict(name="denial", metric="pass_rate", min=0.9,
                                  no_significant_drop=True, blocking=True)])
    loose = copy.deepcopy(spec)
    del loose["slices"][0]["no_significant_drop"]
    assert integrity_check(base, base, loose, spec)


@pytest.mark.parametrize("args", [(0, 0, 1), (5, -1, 2), (5, 6, 2), (5, 1, 6), (5.0, 1, 1), (True, 1, 1)])
def test_advanced_pass_estimators_reject_invalid_inputs(args):
    from lab9.stats import pass_at_k, pass_hat_k
    for fn in (pass_at_k, pass_hat_k):
        with pytest.raises(ValueError):
            fn(*args)
