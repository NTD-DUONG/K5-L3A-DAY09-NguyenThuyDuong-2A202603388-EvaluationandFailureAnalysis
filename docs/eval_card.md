# Eval card — LogiX-VN refund agent

- Eval set: v1; SHA `ae5a90e4901e`; 14 item × 5 seed, 70 trial mỗi report.
- Spec: 1.1; seeds [11, 22, 33, 44, 55]; MockLLM, offline, nhãn tách trong labels_v1.json.
- Git HEAD tại lúc sinh tài liệu: `0c54838c88008af7b139f6c6e9419a187091b71f`; code M1–M4 đang ở working tree, chưa gắn commit riêng.
- SHA256 graders.py: `41de48ab4b2815a828ae8da8ab60e22dadee8c1c477e81ea1647747dfa14f587`; stats.py: `f7276de17e9c3a67b3f6691acf4eeda763109c5c30bf6484ed2bc3caa2601d27`.
- Baseline sinh bằng lab9.eval --shape swarm trên nhánh starter/d09; không phải report lấy từ main đã bảo vệ. CI cần đối chiếu lại swarm và baseline sau khi push.

| Report | Run ID |
|---|---|
| baseline | E-swarm-20261117-ae5a |
| fixed | E-fixed-20261117-ae5a |
| regression | E-seeded_regression-20261117-ae5a |
| pr | E-swarm-20261117-ae5a |

| Metric | Ngưỡng | Blocking | Baseline | Fixed | Regression |
|---|---|---|---|---|---|
| approval_bypass | {"max": 0} | True | 0 | 0 | 0 |
| secret_leak | {"max": 0} | True | 0 | 0 | 0 |
| db_fact_kept | {"min": 0.95} | False | 0.9857 | 1.0 | 0.9286 |
| refund_amount_correct | {"min": 0.95, "no_significant_drop": true} | True | 0.9857 | 1.0 | 0.8571 |
| pass_rate | {"min": 0.85, "no_significant_drop": true} | True | 0.9857 | 1.0 | 0.7143 |
| pass_5 | {"min": 0.8} | False | 0.9286 | 1.0 | 0.7143 |
| cost_per_success | {"max_increase": 0.1} | False | 49.567 | 48.7157 | 81.202 |
| reply_amount_matches_ledger | {"min": 1.0, "no_significant_drop": true} | True | 1.0 | 1.0 | 0.7857 |
| proposal_amount_correct | {"min": 0.95, "no_significant_drop": true} | True | 0.9857 | 1.0 | 0.7857 |

## Paired CI và quyết định gate

| Shape / metric | Δ PR − baseline | CI 95% |
|---|---|---|
| fixed / refund_amount_correct | +0.014 | [+0.000, +0.043] |
| fixed / pass_rate | +0.014 | [+0.000, +0.043] |
| fixed / reply_amount_matches_ledger | +0.000 | [+0.000, +0.000] |
| fixed / proposal_amount_correct | +0.014 | [+0.000, +0.043] |
| regression / refund_amount_correct | -0.129 | [-0.315, +0.000] |
| regression / pass_rate | -0.271 | [-0.500, -0.057] |
| regression / reply_amount_matches_ledger | -0.214 | [-0.429, +0.000] |
| regression / proposal_amount_correct | -0.200 | [-0.414, +0.000] |

- pr: exit 0; blocked: none.

- fixed: exit 0; blocked: none.

- regression: exit 1; blocked: refund_amount_correct, pass_rate, reply_amount_matches_ledger, proposal_amount_correct.

Bootstrap theo item: lấy trung bình 5 seed mỗi item trước, resample cặp cùng item; 1000 resample, percentile, rng=2027. Không coi 70 trial là 70 item độc lập.

Judge tone: κ=0.757, P=0.857, R=0.8; helpful bị loại: κ=0.375, R=0.3.

Trace case: [C-002@11](trace_case.md), bước sai đầu tiên event 3 model_override; regression test test_lab9_trace_case.py. Detection public=100%, false alarms fixed=0%; xem [M3](m3_graders.md).

Gate owner đề xuất: Nguyễn Thùy Dương (người nộp bài); khi exit 1 cần điều tra trace, sửa lỗi và chạy lại trước merge. Chưa ghi nhận phê duyệt release.

Phạm vi: kiểm chứng offline refund ship/hàng hỏng trên public world; chưa cho phép pilot với giao dịch thật. Host chịu trách nhiệm approval, ownership và idempotency.

Giới hạn: 14 item cho CI rộng; MockLLM không đại diện LLM thật; judge replay public chưa có held-out; FM-08 chỉ phân tích định dạng reply public (không đo completeness). Chưa triển khai integrity/ratchet và slice gate M5–M7; chưa xác minh anchor ẩn hoặc CI GitHub.

Đổi item/nhãn/phạm vi eval thì tăng eval_set_version và sinh baseline mới. Đổi metric hoặc ngưỡng thì tăng metric_spec_version; cùng eval set không nới ngưỡng. Khi chuyển model thật cần đo A/A để chọn ngưỡng ngoài dải nhiễu.
