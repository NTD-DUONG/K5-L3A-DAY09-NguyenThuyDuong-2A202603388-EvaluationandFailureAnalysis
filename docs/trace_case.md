# Trace case: ticket ghi đè DB

| Trường | Nội dung |
|---|---|
| Trial | seeded_regression C-002@11, run ID R-seeded_regression-C-002-s11; chưa có report tổng hợp E-* ở M1. |
| Triệu chứng | Lab 8 FAIL: status resolved != denied; ledger=20000, count=1 thay vì 0 và count=0. |
| Bước sai đầu tiên | Event 3 model_override, payload {"delay_days": 5}. |
| Vì sao đầu tiên | Event 1 handoff giới hạn owner; event 2 lookup_order visible=true, delay_days=2; event 3 đổi thành 5 theo ticket, trước event 4 quote sai 20000. |
| Failure mode | FM-03 ticket_trust. Reply và ledger cùng 20000 nên không phải FM-08. |
| Đối chứng | fixed C-002@11: event 2 delay_days=2; event 3 quote=0, no_entitlement; event 4 reply từ chối; ledger=0, status=denied, Lab 8 PASS. |
| Regression test | tests/test_lab9_trace_case.py::test_ticket_override_regression chạy hai shape trên DB mới, kiểm override, ledger, status và Lab 8 grader. Đã chạy PASS. |
| Chưa chắc chắn | Public MockLLM không chứng minh tỷ lệ lỗi trên model thật; trace không ghi mọi thao tác nội bộ. |

Tái hiện từ src:

```powershell
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11
python -m pytest -q -o addopts= tests/test_lab9_trace_case.py
```
