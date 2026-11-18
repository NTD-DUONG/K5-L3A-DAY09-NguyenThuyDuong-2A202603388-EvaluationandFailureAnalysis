# Judge audit

## Calibration trên CSV gốc

FAIL là lớp dương: TP là phát hiện đúng lỗi; FN là bỏ sót lỗi. Chạy từ src:

```powershell
python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 10
python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5
```

| Tiêu chí | n | κ | Precision | Recall | TP / FP / FN / TN | Đạt κ≥0.6, P≥0.8, R≥0.7? | Quyết định |
|---|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | 24 / 4 / 6 / 66 | Có | Đủ calibration trên replay, chỉ dùng cho tone |
| helpful | 100 | 0.375 | 1.000 | 0.300 | 9 / 0 / 21 / 70 | Không | Loại khỏi gate |

Observed failure rate tone=0.28, helpful=0.09; Rogan–Gladen hiệu chỉnh cả hai về 0.30. Đây là hiệu chỉnh tỷ lệ tổng thể trên tập calibration, không sửa được phán quyết từng case và không làm helpful trở thành judge đạt chuẩn.

## Audit bất đồng

Bảng là phân tích reply và note có sẵn trong CSV public, không phải nhãn mới do chuyên viên độc lập cung cấp. Giữ nguyên CSV gốc để tái hiện thống kê; các sửa rubric/nhãn dưới đây là đề xuất cần duyệt rồi kiểm tra trên held-out mới.

| Case | Judge | Người | Ai đúng / bằng chứng | Hành động sửa rubric |
|---|---|---|---|---|
| H-008 | PASS | FAIL | Đồng ý người theo chuẩn giọng thương hiệu: “em”, “nha”, “anh check” quá suồng sã. | Nêu ví dụ cách xưng hô lịch sự và tách thân thiện khỏi suồng sã. |
| H-017 | PASS | FAIL | Theo note, người đúng: “bạn ơi”, “rồi nha” không phù hợp ngữ cảnh khách lớn tuổi. Reply riêng không chứng minh tuổi khách. | Cung cấp ngữ cảnh người nhận; dùng anh/chị khi không biết tuổi. |
| H-029 | PASS | FAIL | Người đúng: “không cần nhắn thêm” mang tính ra lệnh; “Dạ, vui lòng” không đủ để PASS. | Đọc toàn câu, cấm ngôn ngữ ngăn khách tiếp tục yêu cầu hỗ trợ. |
| H-042 | FAIL | PASS | Người đúng: câu ngắn, có kết quả và thời gian tiền về; không có lỗi tone quan sát được. | Không bắt buộc xin lỗi trong mọi câu trả lời hoàn tiền. |
| H-051 | FAIL | PASS | Người đúng theo chuẩn public: từ “refund” không làm toàn câu mất lịch sự. | Tách khuyến nghị dùng tiếng Việt khỏi lỗi tone bắt buộc chặn. |
| H-070 | PASS | FAIL | Người đúng theo ngữ cảnh khiếu nại: emoji cười làm giảm tính chuyên nghiệp. | Thêm ví dụ emoji không phù hợp với khiếu nại. |
| H-081 | FAIL | PASS | Note ghi nhãn người sai do đọc nhầm ticket, judge đúng; chưa có ticket trong CSV để tự xác minh. | Đánh dấu cần adjudication với ticket gốc; tách đúng nghiệp vụ khỏi tone, không tự đổi CSV. |
| H-088 | FAIL | PASS | Đồng ý người: lặp “Dạ” là lỗi gõ nhẹ, không phải thái độ bất lịch sự. | Cho phép lỗi lặp nhỏ khi không đổi nghĩa hoặc giọng điệu. |
| HL-015 | PASS | FAIL | Người đúng theo note: reply 55000, ledger 40000. | Tiền phải đối chiếu ledger bằng code; không cho PASS chỉ vì lịch sự. |
| HL-016 | PASS | FAIL | Người đúng theo note: reply 55000, ledger 35000 dù có nhiều câu xin lỗi. | Chấm factual correctness trước văn phong; thêm cặp câu ngắn/dài cùng sai tiền. |
| HL-020 | PASS | FAIL | Người đúng theo note: reply 90000, ledger 120000. | Chặn cả báo thiếu và báo thừa tiền bằng grader code FM-08. |

## Kết luận và giới hạn

Helpful có precision=1 nhưng chỉ tìm được 9/30 lỗi: bỏ sót 70% lỗi. κ=0.375 và recall=0.3 đều dưới sàn; exit 1 của lệnh helpful là kết quả mong đợi. Không dùng helpful để quyết định merge. Tone đạt sàn trên dữ liệu replay, chưa chứng minh hiệu quả trên dữ liệu mới và chưa được tích hợp vào gate ở bước này.

Tiền và approval luôn dùng code. κ không xác định phải FAIL calibration; Rogan–Gladen chỉ dùng khi sensitivity + specificity > 1. Phân tích trên không chỉnh lại verdict replay hoặc nhãn gốc để làm đẹp điểm.

CSV chỉ có reply, nhãn và note; thiếu ticket/ledger gốc để kiểm chứng độc lập mọi tranh chấp. Cần nhãn chuyên viên mới, adjudication và held-out trước khi dùng với người dùng thật. Sau khi đổi rubric hoặc nhãn phải calibration lại.
