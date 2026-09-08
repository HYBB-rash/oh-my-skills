"""Bounded CLI regression checks. Artifacts go only to the supplied new output directory."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys

from render import render

ROOT = Path(__file__).resolve().parent
SOURCE = """# 社区图书室九月观察\n\n## 到访记录\n连续 7 天记录的日均到访人数为 38 人，上一个 7 天为 32 人。同期进入开学周，不能据此认定延长开放时间造成了增长。\n\n## 使用限制\n记录仅覆盖到访人次，没有去重，也没有测量满意度。后续是否保留晚间开放尚未决定。\n"""
PACKET = {"title": "图书室到访增加，原因仍待判断", "question": "这两周的到访记录说明什么？", "answer": "日均到访从 32 人增加到 38 人，但同期进入开学周，原因尚不能确定。", "boundary": "仅有两个连续 7 天的到访人次记录，没有去重或测量满意度。", "cases": [{"question": "人数增加是否证明延时开放有效？", "title": "记录显示增加，不能单独确定原因", "explanation": ["连续 7 天的日均到访为 38 人，上一个 7 天为 32 人；同期进入开学周，存在另一种可能的解释。", "没有去重的人次不能等同于独立读者数量，也不能据此判断满意度。"], "limit": "后续是否保留晚间开放尚未决定。", "source_section": "到访记录"}, {"question": "这些记录还不能回答什么？", "title": "独立读者数量与满意度均未测量", "explanation": ["记录仅覆盖到访人次，没有去重，也没有测量满意度。"], "limit": "后续是否保留晚间开放尚未决定。", "source_section": "使用限制"}]}


def invoke(args, cwd=None, env=None, value=None):
    return subprocess.run([str(x) for x in args], cwd=cwd, env={**os.environ, **(env or {})}, input=None if value is None else json.dumps(value, ensure_ascii=False), capture_output=True, text=True, timeout=38)


def decoded(proc):
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    return json.loads(proc.stdout)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    results = []

    def record(name, ok, **evidence):
        results.append({"name": name, "passed": bool(ok), **evidence})
        (output / "test-results.json").write_text(json.dumps({"passed": all(x["passed"] for x in results), "checks": results}, ensure_ascii=False, indent=2))
        assert ok, (name, evidence)

    def fixture(name, transform=lambda page: page, packet=None, env=None):
        folder = output / name
        folder.mkdir()
        content = packet or PACKET
        (folder / "source.md").write_text(SOURCE)
        (folder / "packet.json").write_text(json.dumps(content, ensure_ascii=False))
        (folder / "report.html").write_text(transform(render(content, SOURCE)))
        result = decoded(invoke(["node", ROOT / "review.mjs", folder], env=env))
        return folder, Path(result["review_directory"]), result

    def verdict(review):
        value = json.loads((review / "review-request.json").read_text())["submission"]
        value["reviewer"] = "Automated contract fixture; no semantic or visual acceptance"
        for group in ["semantic", "visual"]:
            for item in value[group].values():
                item["reason"] = "Not reviewed; this is a mechanical contract test."
        return value

    normal, normal_review, baseline = fixture("no-comparison")
    record("ordinary_report_without_forced_comparison", baseline["machine_status"] == "passed" and 'class="choice-lab"' not in (normal / "report.html").read_text(), machine_seconds=baseline["machine_seconds"])
    compare = copy.deepcopy(PACKET)
    compare["cases"][0]["comparison"] = {"basis": "原文两个连续 7 天的记录", "left_label": "上一周", "left": "日均 32 人", "right_label": "本周", "right": "日均 38 人", "why": "到访记录增加；同期进入开学周，不能确定原因。"}
    compare["tradeoff"] = {"question": "记录可以回答什么？", "basis": "到访记录与使用限制", "choices": [{"label": "到访人次", "outcome": "有记录", "reason": "原文逐周统计了到访人次。"}, {"label": "满意度", "outcome": "无法判断", "reason": "原文没有测量满意度。"}]}
    _, _, comparative = fixture("with-comparison", packet=compare)
    record("supported_comparison_controls_and_layout", comparative["machine_status"] == "passed")
    _, broken, result = fixture("broken-interaction", lambda page: re.sub(r"<script>.*?</script>", "", page, flags=re.S))
    record("broken_interaction_is_failed", result["machine_status"] == "failed" and "Question c0" in result["error"])
    _, _, result = fixture("overflow", lambda page: page.replace("</head>", "<style>body{min-width:1600px!important}</style></head>"))
    record("horizontal_overflow_is_failed", result["machine_status"] == "failed" and "overflow" in result["error"])
    _, missing, result = fixture("missing-browser", env={"REPORT_CHROME_BIN": "/no-such-readable-report-browser"})
    record("missing_browser_is_incomplete_without_auto_retry", result["machine_status"] == "incomplete" and json.loads((missing / "machine.json").read_text())["automatic_retries"] == 0)
    unavailable = verdict(missing)
    unavailable["visual"]["desktop"]["status"] = "passed"
    proc = invoke(["node", ROOT / "review.mjs", "finish", missing], value=unavailable)
    record("unavailable_screenshot_cannot_pass", proc.returncode != 0 and "Image unavailable" in proc.stderr)
    result = decoded(invoke(["node", ROOT / "review.mjs", "finish", missing], value=verdict(missing)))
    record("missing_tool_finishes_as_incomplete", result["status"] == "incomplete")
    value = verdict(normal_review)
    partial = copy.deepcopy(value)
    del partial["semantic"]["coverage"]
    proc = invoke(["node", ROOT / "review.mjs", "finish", normal_review], value=partial)
    record("missing_checklist_rejected_and_archived", proc.returncode != 0 and "checklist" in proc.stderr and len(list((normal_review / "submissions").glob("*/submission.txt"))) == 1)
    invented = copy.deepcopy(value)
    invented["semantic"]["fidelity"].update(status="passed", source_excerpt="这是一段原文不存在的引句。", output_excerpt=PACKET["answer"])
    proc = invoke(["node", ROOT / "review.mjs", "finish", normal_review], value=invented)
    record("invented_quote_rejected_and_archived", proc.returncode != 0 and "Source excerpt" in proc.stderr and len(list((normal_review / "submissions").glob("*/submission.txt"))) == 2)
    before = {name: digest(normal / name) for name in ["source.md", "packet.json", "report.html"]}
    corrected = copy.deepcopy(invented)
    corrected["semantic"]["fidelity"]["source_excerpt"] = "同期进入开学周，不能据此认定延长开放时间造成了增长。"
    result = decoded(invoke(["node", ROOT / "review.mjs", "finish", normal_review], value=corrected))
    record("correct_only_review_preserves_content_and_unreviewed_is_incomplete", result["status"] == "incomplete" and before == {name: digest(normal / name) for name in before})
    before_receipt = digest(normal_review / "receipt.json")
    proc = invoke(["node", ROOT / "review.mjs", "finish", normal_review], value=corrected)
    record("duplicate_finish_does_not_overwrite_receipt", proc.returncode != 0 and digest(normal_review / "receipt.json") == before_receipt)
    result = decoded(invoke(["node", ROOT / "review.mjs", "finish", broken], value=verdict(broken)))
    record("real_defect_remains_failed", result["status"] == "failed")
    changed, review, _ = fixture("changed-input")
    (changed / "report.html").write_text((changed / "report.html").read_text() + "\n<!-- changed -->")
    proc = invoke(["node", ROOT / "review.mjs", "finish", review], value=verdict(review))
    record("changed_input_rejected", proc.returncode != 0 and "Original input changed" in proc.stderr)
    _, review, _ = fixture("changed-image")
    (review / "mobile.png").write_bytes(b"changed")
    proc = invoke(["node", ROOT / "review.mjs", "finish", review], value=verdict(review))
    record("changed_screenshot_rejected", proc.returncode != 0 and "Screenshot evidence changed" in proc.stderr)
    source = output / "input.md"
    source.write_text(SOURCE)
    work = output / "retry-work"
    decoded(invoke([sys.executable, ROOT / "report.py", "init", source, "--work", work]))
    actual_producer = json.loads((work / "receipt.json").read_text())["producer"]
    record("unselected_model_is_recorded_as_unknown", actual_producer["model"] == "unknown" and actual_producer["effort"] == "unknown")
    (work / "draft.json").write_text(json.dumps(PACKET, ensure_ascii=False))
    result = decoded(invoke(["./rr", "submit"], cwd=work, env={"REPORT_NODE_BIN": "/no-such-readable-report-node"}))
    before = {name: digest(work / name) for name in ["submission.txt", "packet.json", "report.html"]}
    (work / "draft.json").write_text('{"title":"a model accidentally replaced the draft"}')
    result2 = decoded(invoke(["./rr", "retry"], cwd=work))
    record("retry_missing_tool_uses_original_saved_bytes", result["status"] == "incomplete" and result2["machine_status"] == "passed" and before == {name: digest(work / name) for name in before})
    review = Path(json.loads((work / "receipt.json").read_text())["review_directory"])
    value = verdict(review)
    (work / "verdict.json").write_text(json.dumps(value))
    result = decoded(invoke(["./rr", "finish"], cwd=work, env={"REPORT_NODE_BIN": "/no-such-readable-report-node"}))
    (work / "verdict.json").write_text("overwritten after failure")
    result2 = decoded(invoke(["./rr", "retry"], cwd=work))
    record("finish_retry_reuses_saved_review_without_rerunning_machine", result["status"] == "incomplete" and result2["status"] == "incomplete" and len(list((work / "reviews").iterdir())) == 1 and len(list((work / "review-submissions").iterdir())) == 2)
    (work / "submission.txt").write_text("tampered")
    proc = invoke(["./rr", "retry"], cwd=work)
    # status-only reads do not claim a fresh check; submit checks the saved content hash.
    proc = invoke(["./rr", "submit"], cwd=work)
    record("saved_content_tampering_rejected", proc.returncode != 0 and "changed" in proc.stdout)
    malformed = output / "malformed"
    decoded(invoke([sys.executable, ROOT / "report.py", "init", source, "--work", malformed]))
    (malformed / "draft.json").write_text('{"broken"')
    result = decoded(invoke(["./rr", "submit"], cwd=malformed))
    record("malformed_first_submission_is_preserved", result["status"] == "incomplete" and (malformed / "submission.txt").read_text() == '{"broken"')
    print(json.dumps({"passed": True, "checks": len(results), "results_file": str(output / "test-results.json")}))


if __name__ == "__main__":
    main()
