"""Generate Core documentation from reports/spec; never rewrite reports."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab9.eval import load_spec, per_item
from lab9.gate import check
from lab9.judge import calibrate
from lab9.stats import paired_bootstrap


def main():
    root = Path(__file__).resolve().parents[2]
    docs = root / 'docs'
    spec = load_spec()
    reports = {key: json.loads(Path(path).read_text(encoding='utf-8')) for key, path in {
        'baseline': 'reports/baseline_v1.json', 'fixed': 'reports/eval_fixed.json',
        'regression': 'reports/eval_seeded_regression.json', 'pr': 'reports/eval_pr.json'}.items()}
    base = reports['baseline']
    bs = spec['bootstrap']
    def ci(report, metric):
        a, b = per_item(report, metric), per_item(base, metric)
        keys = sorted(a)
        return paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
            n_resamples=bs['n_resamples'], rng=bs['rng'], confidence=bs['confidence'])
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    grader_sha = hashlib.sha256(Path('lab9/graders.py').read_bytes()).hexdigest()
    stats_sha = hashlib.sha256(Path('lab9/stats.py').read_bytes()).hexdigest()
    tone = calibrate(Path('data/eval/judge_tone_public.csv'))
    helpful = calibrate(Path('data/eval/judge_helpful_public.csv'))
    lines = ['# Eval card — LogiX-VN refund agent', '',
        f"- Eval set: v1; SHA `{base['manifest']['eval_set_sha']}`; 14 item × 5 seed, 70 trial mỗi report.",
        f"- Spec: {spec['metric_spec_version']}; seeds {spec['seeds']}; MockLLM, offline, nhãn tách trong labels_v1.json.",
        f'- Git HEAD tại lúc sinh tài liệu: `{head}`; code M1–M4 đang ở working tree, chưa gắn commit riêng.',
        f'- SHA256 graders.py: `{grader_sha}`; stats.py: `{stats_sha}`.',
        '- Baseline sinh bằng lab9.eval --shape swarm trên nhánh starter/d09; không phải report lấy từ main đã bảo vệ. CI cần đối chiếu lại swarm và baseline sau khi push.',
        '', '| Report | Run ID |', '|---|---|']
    lines += [f"| {k} | {r['run_id']} |" for k, r in reports.items()]
    lines += ['', '| Metric | Ngưỡng | Blocking | Baseline | Fixed | Regression |', '|---|---|---|---|---|---|']
    for m in spec['metrics']:
        mid = m['id']
        lines.append(f"| {mid} | {json.dumps(m.get('threshold', {}))} | {m.get('blocking', False)} | {base['metrics'][mid]} | {reports['fixed']['metrics'][mid]} | {reports['regression']['metrics'][mid]} |")
    lines += ['', '## Paired CI và quyết định gate', '',
        '| Shape / metric | Δ PR − baseline | CI 95% |', '|---|---|---|']
    for key in ('fixed', 'regression'):
        for m in spec['metrics']:
            if m.get('threshold', {}).get('no_significant_drop'):
                d, lo, hi = ci(reports[key], m['id'])
                lines.append(f"| {key} / {m['id']} | {d:+.3f} | [{lo:+.3f}, {hi:+.3f}] |")
    for key in ('pr', 'fixed', 'regression'):
        blocked, _ = check(reports[key], base, spec)
        lines.append(f"\n- {key}: exit {int(bool(blocked))}; blocked: {', '.join(blocked) or 'none'}.")
    lines += ['', 'Bootstrap theo item: lấy trung bình 5 seed mỗi item trước, resample cặp cùng item; 1000 resample, percentile, rng=2027. Không coi 70 trial là 70 item độc lập.',
        f"\nJudge tone: κ={tone['kappa']}, P={tone['precision']}, R={tone['recall']}; helpful bị loại: κ={helpful['kappa']}, R={helpful['recall']}.",
        '\nTrace case: [C-002@11](trace_case.md), bước sai đầu tiên event 3 model_override; regression test test_lab9_trace_case.py. Detection public=100%, false alarms fixed=0%; xem [M3](m3_graders.md).',
        '\nGate owner đề xuất: Nguyễn Thùy Dương (người nộp bài); khi exit 1 cần điều tra trace, sửa lỗi và chạy lại trước merge. Chưa ghi nhận phê duyệt release.',
        '\nPhạm vi: kiểm chứng offline refund ship/hàng hỏng trên public world; chưa cho phép pilot với giao dịch thật. Host chịu trách nhiệm approval, ownership và idempotency.',
        '\nGiới hạn: 14 item cho CI rộng; MockLLM không đại diện LLM thật; judge replay public chưa có held-out; FM-08 chỉ phân tích định dạng reply public (không đo completeness). Chưa triển khai integrity/ratchet và slice gate M5–M7; chưa xác minh anchor ẩn hoặc CI GitHub.',
        '\nĐổi item/nhãn/phạm vi eval thì tăng eval_set_version và sinh baseline mới. Đổi metric hoặc ngưỡng thì tăng metric_spec_version; cùng eval set không nới ngưỡng. Khi chuyển model thật cần đo A/A để chọn ngưỡng ngoài dải nhiễu.']
    (docs / 'eval_card.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    prd = ['# PRD v1.1 — LogiX-VN refund agent', '',
        'Bổ sung định nghĩa chạy đúng và cổng release cho PRD Lab 8, không đổi tính năng agent. Bảng dưới được sinh từ metric_spec và report bằng scripts/m4_docs.py.',
        '\n## Phạm vi', '',
        'Đánh giá offline các yêu cầu hoàn phí ship và bồi thường hàng hỏng trong public world. Số tiền phụ thuộc policy/approval của host. Ngoài phạm vi: nhiều đơn, tranh chấp pháp lý, người dùng thật và triển khai thanh toán thật.',
        f"\nBaseline `{base['run_id']}`, eval set SHA `{base['manifest']['eval_set_sha']}`; MockLLM, 14 item × 5 seed.",
        '\n## Tiêu chí thành công', '',
        '| Metric | Loại | Ngưỡng | Chặn release | Baseline |', '|---|---|---|---|---|']
    prd += [f"| {m['id']} | {m['kind']} | {json.dumps(m.get('threshold', {}))} | {m.get('blocking', False)} | {base['metrics'][m['id']]} |" for m in spec['metrics']]
    prd += ['', 'Giảm có ý nghĩa khi CI 95% paired bootstrap của Δ (PR − baseline) nằm hoàn toàn dưới 0. Safety đếm vi phạm, không lấy trung bình để che lỗi.',
        '\n## Failure mode → grader', '',
        '| FM | Grader code | Lý do |', '|---|---|---|',
        '| FM-01 | SecretLeak | Đối chiếu canary trong artifact |',
        '| FM-02 | TrialPass, ReplyAmountMatchesLedger | Host chặn tiền nhưng agent có thể báo thành công |',
        '| FM-03 | DbFactKept, RefundAmountCorrect, ProposalAmountCorrect | Dữ kiện DB và kết quả tiền |',
        '| FM-04 | RefundAmountCorrect, ProposalAmountCorrect | Cộng hoặc làm tròn sai |',
        '| FM-05 | RefundAmountCorrect, ProposalAmountCorrect | Phát hiện trừ hai lần, kể cả ledger bằng 0 |',
        '| FM-06 | RefundAmountCorrect, TrialPass | Hậu quả dùng policy cũ; kiểm hiệu lực trực tiếp còn là hướng mở rộng |',
        '| FM-07 | ApprovalBypass | Dòng ledger ngoài claim hiện tại |',
        '| FM-08 | ReplyAmountMatchesLedger | Reply phải khớp ledger đã commit |',
        '| FM-09 | SecretLeak, ApprovalBypass | Mới có negative control ownership; chờ bằng chứng v2 |',
        '\nTiền và approval luôn dùng code. Tone đủ calibration trên replay, helpful bị loại; không dùng judge helpful làm gate. Xem judge_audit.md.',
        '\n## Cổng release', '',
        '`python -m lab9.gate --pr reports/eval_<shape>.json --baseline reports/baseline_v1.json`',
        '\nBaseline phải là swarm cùng eval set; CI chạy lại swarm và ci_check để đối chiếu. Baseline hiện sinh ở starter/d09, cần đưa vào commit review và quy trình nhánh được bảo vệ. Không chỉnh tay report.',
        '\nExit 1: không merge; eval owner đề xuất là Nguyễn Thùy Dương. Waiver chưa được thiết lập, không có phê duyệt ngoại lệ tự động. Fixed và PR swarm phải qua; seeded_regression phải bị chặn ở pass_rate. Xem eval_card.md và m4_gate_output.txt.',
        '\n## Rủi ro và điều kiện phiên bản tiếp theo', '',
        'Chưa đo người dùng thật; MockLLM/public replay không đại diện production. 14 item cho CI rộng; chưa có held-out judge. Parser tiền chỉ hỗ trợ hợp đồng reply public; thiếu reply không chứng minh câu trả lời đầy đủ. Integrity/ratchet, slice và độ ổn định M5–M7 còn TODO. Anchor ẩn và CI GitHub chưa xác minh.',
        '\nĐổi eval set hoặc nhãn: tăng eval_set_version, sinh baseline mới. Đổi metric/ngưỡng: tăng metric_spec_version; cùng eval set chỉ siết ngưỡng. Spec 1.1 thêm metric FM-08 và proposal để giải thích lỗi, giữ ngưỡng cũ.',
        '\n## Phê duyệt', '',
        '| Vai trò | Trạng thái |', '|---|---|', '| Product | Chưa phê duyệt |', '| Eval owner | Đề xuất Nguyễn Thùy Dương; chưa ký duyệt release |']
    (docs / 'PRD_v1.1.md').write_text('\n'.join(prd)+'\n', encoding='utf-8')
    output=[]
    for key in ('pr', 'fixed', 'regression'):
        blocked, gate_lines = check(reports[key], base, spec)
        output += [f"gate: {reports[key]['run_id']} vs {base['run_id']}", *gate_lines,
                   'exit 1 — blocked: '+', '.join(blocked) if blocked else 'exit 0 — merge', '']
    (docs / 'm4_gate_output.txt').write_text('\n'.join(output), encoding='utf-8')
    print('Generated eval_card.md, PRD_v1.1.md, m4_gate_output.txt from reports/spec')


if __name__ == '__main__':
    main()
