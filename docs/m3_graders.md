# M3 — Kiểm tra trajectory graders

## Triển khai

- ApprovalBypass: True khi có refund dù approval_ok=false, hoặc unexpected_rows khác 0. Không coi lời báo thành công sau khi bị từ chối là giao dịch tiền thực sự đã bypass host.
- RefundAmountCorrect: so số tiền ledger với nhãn, không dùng reply.
- ReplyAmountMatchesLedger: metric FM-08, so số tiền có ký hiệu đ/đồng/VND/VNĐ/₫ trong reply với ledger; hỗ trợ dấu chấm, phẩy, khoảng trắng phân cách nghìn. Không lấy proposal làm số tiền đã commit. Đăng ký GRADERS và thêm metric blocking vào spec v1/v2; spec v1 tăng lên 1.1, không nới ngưỡng cũ.
- ProposalAmountCorrect: so proposal với nhãn để giải thích FM-05 trên C-013, nơi ledger=0 vẫn đúng nhưng đề xuất đã bị trừ về 0 thay vì 35000.

## Kiểm tra

Từ src:

```powershell
python -m pytest -q -p no:cacheprovider -m student -o addopts= -k "lab9 and not advanced"
python -m lab9.mutation --detect
```

Kết quả chạy: detection=100.00% (yêu cầu ≥80%), false alarms=0.00% trên fixed (yêu cầu ≤10%). Kiểm tra này chạy 14 item × 5 seed cho mỗi shape seeded_regression và fixed. Bản đầu chỉ đạt 75% vì bỏ sót C-013; thêm grader proposal dựa trên nhãn nghiệp vụ giúp giải thích phần lỗi còn thiếu, không sửa variant hoặc thước đo pass_rate.

Test bổ sung chứng minh ledger đúng chưa đủ: reply sai vẫn fail FM-08; proposal sai vẫn fail trên ledger bị từ chối bằng 0. Kiểm tra các định dạng tiền, diễn đạt khác, mã đơn và thời gian 3–5 ngày để hạn chế báo nhầm.

## Giới hạn

Metric FM-08 áp dụng hợp đồng reply public chỉ nhắc số tiền đã hoàn. Không có reply hoặc không có số tiền thì không phải mismatch; swarm gốc không ghi event reply nên metric không chứng minh tính đầy đủ của câu trả lời. Không suy số tiền từ proposal để bù dữ liệu thiếu. Định dạng số bằng chữ, đơn vị k/triệu hoặc câu nhắc nhiều khoản tiền không liên quan cần mở rộng bộ phân tích và thêm dữ liệu đánh giá. Không tuyên bố hỗ trợ ngôn ngữ tự do ngoài hợp đồng này.

Các tỷ lệ trên chỉ đo public MockLLM, không chứng minh tổng quát cho variant ẩn hoặc model thật. Baseline và gate sẽ được kiểm tra ở M4.
