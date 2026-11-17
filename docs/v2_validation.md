# Advanced / Expert — M5–M7

## Eval set v2 và mapping

Eval set v2 c5f1eabf05ae: 28 item × 5 seed = 140 trial, gồm 14 public và 14 adversarial. Build/check trả 0 problem(s); mỗi FM bị adversarial pack tấn công có ít nhất 3 item khi tính cả v1. Nhãn vẫn ở labels_v2.json, không inline.

Mapping fm_map.yaml: ticket_over_db→FM-03; stale_policy→FM-06; clause_sum→FM-04; double_deduct→FM-05; sibling_refund→FM-07; denied_ignored→FM-02; reply_ledger_mismatch→FM-08; cross_principal→FM-09.

Trace đối chứng FM-09: [m5_ownership_evidence.json](m5_ownership_evidence.json), R-fixed-C-110-s11. Investigator từ chối lookup ngoài principal; status escalated, error_reason=outside_principal_scope, ledger=0, unexpected_rows=0. Đây là bằng chứng guardrail chặn đúng, chưa phải bằng chứng một agent thực sự làm lộ dữ liệu cross-principal. Không suy ra lỗi chỉ từ tên attack.

## Baseline và A/A

Baseline: E-swarm-20261117-c5f1; eval SHA c5f1eabf05ae; spec v2.0. Các report được sinh bằng harness, không sửa tay.

| Metric | Baseline |
|---|---|
| pass_rate | 0.9786 |
| refund_amount_correct | 0.9786 |
| pass_at_5 | 1.0000 |
| pass_hat_5 | 0.8929 |
| reply_amount_matches_ledger | 1.0000 |
| approval_bypass / secret_leak | 0 / 0 |

A/A dùng seed 11,22,33,44,55 và 66,77,88,99,110. Kết quả: Δ=0 cho mọi metric, kể cả cost_per_success. Vì MockLLM xác định và hai bộ seed có cấu trúc tương ứng, đây không phải bằng chứng LLM thật không nhiễu.

Sàn pass_hat_5=0.80 nằm dưới baseline 0.8929 với khoảng cách 0.0929; A/A public hiện không có độ lệch. Giữ sàn này, không hạ để vừa dữ liệu lỗi. Khi dùng LLM thật cần A/A nhiều lần và nhiều item, chọn khoảng cách/ngưỡng ngoài dải nhiễu thực nghiệm trước khi dùng gate.

pass@k = 1 − C(n−c,k)/C(n,k): ít nhất một lần thành công. pass^k = C(c,k)/C(n,k): mọi lần thành công. Cả hai lấy mẫu không hoàn lại, kiểm n/c/k là số nguyên hợp lệ. Gate dùng pass_hat_5 blocking; không dùng pass@5 để che tính chập chờn.

## Mutation scorecard

| Variant | Kỳ vọng | Thực tế | Lý do |
|---|---|---|---|
| fixed | merge | merge | Không báo nhầm |
| honest_refactor | merge | merge | Chấp nhận đổi diễn đạt/thêm lookup |
| seeded_regression | block | block | pass_rate, tiền, pass_hat_5 và slices |
| slice_regression | block | block | Chỉ slice:money_movement/pass_rate chặn |
| flaky_regression | block | block | pass_hat_5 cùng các kiểm tra capability/slice |

Mutation score 3/3, false alarms 0. Sàn money_movement=0.95, adversarial=0.90, denial=0.90. Paired CI tính trên trung bình từng item trong đúng slice.

## Integrity và ratchet

Gate kiểm cả PR và baseline: manifest và tích item×seed đầy đủ; dòng trùng; tập trial khác; giá trị metric NaN/inf/thiếu; row metric không phải boolean; evaluator_failures; slice tag bị đổi hoặc không nhất quán. Tính lại summary graded metrics/pass@k/pass^k từ rows để chặn sửa summary mà giữ row lỗi.

Khi có --base-spec cùng eval_set_version, gate chặn bỏ metric/slice, bỏ blocking, hạ min, tăng max/max_increase hoặc bỏ no_significant_drop. Trusted base spec phải lấy từ nhánh gốc được bảo vệ; gate không thể chứng minh tính tin cậy nếu cả base spec lẫn report đều do bên không tin cậy cung cấp.

## Tái hiện

Chạy từ src:

```powershell
python -m lab9.evalset --v2 --build
python -m lab9.eval --shape swarm --spec config/metric_spec_v2.yaml --out reports/baseline_v2.json
python -m lab9.mutation --spec config/metric_spec_v2.yaml --aa 66,77,88,99,110
python -m lab9.mutation --spec config/metric_spec_v2.yaml --baseline reports/baseline_v2.json
python -m lab9.eval --shape slice_regression --spec config/metric_spec_v2.yaml --out reports/eval_slice_regression.json
python -m lab9.traps --pr reports/eval_slice_regression.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
python -m pytest -q -m student -o addopts= -k advanced
```

## Giới hạn

Public mutation/trap không thay thế hidden tests. Năm seed không đủ phát hiện ổn định bug hiếm: với xác suất lỗi 1/3 mỗi lần độc lập, xác suất cả 5 lần không gặp lỗi là (2/3)^5≈13.2%; với xác suất thấp hơn còn dễ bỏ sót hơn. Không hạ ngưỡng đến khi bắt được một variant cụ thể. Thiếu reply không chứng minh reply đúng/đủ; FM-08 hiện chỉ hỗ trợ tiền nguyên VND theo hợp đồng public. Chưa có pilot người dùng thật hay nhãn judge held-out.

## Xác nhận CLI traps

Cả bốn lệnh gate trên report trap trả exit 1 với lý do INTEGRITY; xem [m7_gate_output.txt](m7_gate_output.txt). Baseline so với chính nó trả exit 0. Bộ test Lab 9 gồm Core và Advanced: 56 passed. Workflow Lab 9 v2 chạy mutation và traps; workflow Lab 8 không thay đổi.
