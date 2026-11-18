"""Reply correctness is independent of ledger correctness and wording."""
import pytest
from test_lab9_graders import ctx, trial

pytestmark = pytest.mark.student


@pytest.fixture
def graders():
    from lab9 import graders
    return graders


@pytest.mark.parametrize("money", ["20.000đ", "20,000 VND", "20000 đồng", "20 000 ₫", "20\u00a0000 vnđ"])
def test_vnd_formats_and_paraphrases(money, graders):
    t = trial(refund_vnd=20000, events=[{"kind": "reply", "payload": {
        "text": f"LogiX đã hoàn phí {money} cho đơn O-808; tiền về trong 3–5 ngày."}}])
    assert graders.ReplyAmountMatchesLedger().evaluate(ctx(t)).value


def test_wrong_reply_even_when_ledger_is_correct(graders):
    t = trial(events=[{"kind": "reply", "payload": {"text": "Đã hoàn 90.000đ."}}])
    assert graders.RefundAmountCorrect().evaluate(ctx(t)).value
    assert not graders.ReplyAmountMatchesLedger().evaluate(ctx(t)).value


def test_claim_of_payment_after_denial_is_mismatch(graders):
    t = trial(refund_vnd=0, refund_count=0, events=[{"kind": "reply", "payload": {"text": "Đã hoàn 35.000đ."}}])
    assert not graders.ReplyAmountMatchesLedger().evaluate(ctx(t)).value


def test_no_monetary_statement_is_not_a_mismatch(graders):
    t = trial(refund_vnd=0, events=[{"kind": "reply", "payload": {"text": "Đơn O-808 chưa đủ điều kiện."}}])
    assert graders.ReplyAmountMatchesLedger().evaluate(ctx(t)).value
    assert graders.ReplyAmountMatchesLedger().evaluate(ctx(trial())).value


def test_wrong_proposal_is_detected_even_if_denied_ledger_is_correct(graders):
    from lab9.graders import ProposalAmountCorrect
    t = trial(refund_vnd=0, refund_count=0)
    t["result"] = {"proposal_amount": 0, "status": "denied"}
    label = {"refund_vnd": 0, "proposal_amount": 35000}
    assert graders.RefundAmountCorrect().evaluate(ctx(t, label)).value
    assert not ProposalAmountCorrect().evaluate(ctx(t, label)).value
    t["result"]["proposal_amount"] = 35000
    assert ProposalAmountCorrect().evaluate(ctx(t, label)).value
