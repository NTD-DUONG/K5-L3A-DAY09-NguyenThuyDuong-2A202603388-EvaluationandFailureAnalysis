"""Replay one isolated public bug at a time, without editing Lab 8 or variants.

Run from src: python scripts/m1_evidence.py
Output is diagnostic evidence, not an eval report or a replacement baseline.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lab8.shapes import SHAPES
from lab9.trace_case import investigate
from lab9.variant_agent import make_shape

CASES = [
    ("FM-01", "leaky_trace", "C-010"),
    ("FM-02", "ignore_denied", "C-007"),
    ("FM-03", "ticket_trust", "C-002"),
    ("FM-04", "sum_parts", "C-014"),
    ("FM-05", "pre_deducted", "C-014"),
    ("FM-06", "stale_clause", "C-006"),
    ("FM-07", "sibling_refund", "C-001"),
    ("FM-08", "misreport", "C-008"),
]


def main():
    for fm, bug, claim in CASES:
        name = f"evidence_{bug}"
        SHAPES[name] = make_shape(name, {"no_override", bug})
        observed = investigate(name, claim, 11)
        control = investigate("fixed", claim, 11)
        print(json.dumps({"failure_mode": fm, "observed": observed,
                          "control": control}, ensure_ascii=True))


if __name__ == "__main__":
    main()
