"""End-to-end regression for ticket overriding database entitlement."""
import pytest

pytestmark = pytest.mark.student


def test_ticket_override_regression():
    from lab9.trace_case import investigate

    bad = investigate("seeded_regression", "C-002", 11)["trial"]
    fixed = investigate("fixed", "C-002", 11)["trial"]
    assert bad["events"][1]["payload"]["lookup_order"]["order"]["delay_days"] == 2
    assert bad["events"][2] == {"kind": "model_override", "payload": {"delay_days": 5}}
    assert bad["snapshot"]["refund_vnd"] == 20000
    assert bad["result"]["status"] == "resolved"
    assert not bad["lab8_pass"]
    assert not any(e["kind"] == "model_override" for e in fixed["events"])
    assert fixed["snapshot"]["refund_vnd"] == 0
    assert fixed["snapshot"]["refund_count"] == 0
    assert fixed["result"]["status"] == "denied"
    assert fixed["lab8_pass"]
