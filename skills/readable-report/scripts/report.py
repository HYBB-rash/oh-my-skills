#!/usr/bin/env python3
"""A short, resumable local interface; raw content and review attempts are retained."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import subprocess
import sys
import uuid

from render import render

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "scripts/review.mjs"


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, value):
    pending = path.with_suffix(path.suffix + ".pending")
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pending.replace(path)


def toolchain():
    return {str(p.relative_to(ROOT)): digest(p) for p in [ROOT / "scripts/report.py", ROOT / "scripts/render.py", CHECKER, ROOT / "scripts/review-contract.json", ROOT / "assets/report.css", ROOT / "assets/behavior.js", ROOT / "references/editor.txt"]}


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def init(args):
    source = args.source.resolve(strict=True)
    raw = source.read_bytes()
    raw.decode("utf-8")
    if not raw.strip():
        raise ValueError("Source is empty")
    work = args.work.resolve()
    if work.exists() and any(work.iterdir()):
        raise ValueError("Use a new, empty work directory; existing material will not be overwritten")
    work.mkdir(parents=True, exist_ok=True)
    (work / "source.md").write_bytes(raw)
    launcher = f"#!{sys.executable}\nimport sys\nsys.path.insert(0, {str(ROOT / 'scripts')!r})\nfrom report import main\nmain()\n"
    (work / "rr").write_text(launcher)
    (work / "rr").chmod(0o755)
    receipt = {"version": "readable-report-v1", "id": uuid.uuid4().hex, "started_at": now(), "status": "awaiting_content", "source_origin": str(source), "source_sha256": digest(work / "source.md"), "requested_producer": {"model": "gpt-5.6-luna", "effort": "medium"}, "producer": {"model": args.producer_model, "effort": args.producer_effort, "evidence": args.producer_evidence}, "toolchain": toolchain(), "human_acceptance": "not recorded", "timings": {}}
    save(work / "receipt.json", receipt)
    emit({"status": receipt["status"], "working_directory": str(work), "next": ["./rr", "context"], "commands": {"submit": "./rr submit", "retry_failed_step": "./rr retry", "finish": "./rr finish", "status": "./rr status"}})


class Run:
    def __init__(self):
        self.folder = Path.cwd()
        self.path = self.folder / "receipt.json"
        self.receipt = read(self.path)
        if self.receipt.get("version") != "readable-report-v1":
            raise ValueError("Run ./rr inside the work directory returned by init")

    def update(self, **values):
        self.receipt.update(values)
        save(self.path, self.receipt)

    def consistent(self):
        if digest(self.folder / "source.md") != self.receipt["source_sha256"]:
            raise ValueError("Saved source changed; create a new work directory")
        if toolchain() != self.receipt["toolchain"]:
            raise ValueError("Skill implementation changed; create a new work directory")
        for name, value in self.receipt.get("saved_hashes", {}).items():
            if digest(self.folder / name) != value:
                raise ValueError(f"Saved {name} changed; create a new work directory")

    def failure(self, step, error):
        attempt = self.folder / "attempts" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + "-" + step)
        attempt.mkdir(parents=True)
        save(attempt / "result.json", {"step": step, "status": "incomplete", "error": str(error), "at": now()})
        self.update(status="incomplete", failed_step=step, error=str(error), last_failure_at=now())
        emit({"status": "incomplete", "failed_step": step, "error": str(error), "next": "./rr retry", "receipt": str(self.path)})

    def context(self):
        self.consistent()
        self.update(context_opened_at=self.receipt.get("context_opened_at", now()))
        print((ROOT / "references/editor.txt").read_text())
        print("\n当前工作目录已经固定。只使用 ./rr 和本目录内的短文件名。\n<source>\n" + (self.folder / "source.md").read_text() + "\n</source>")

    def submit(self):
        self.consistent()
        if (self.folder / "submission.txt").exists():
            emit({"status": self.receipt["status"], "next": "Content is already saved. Use ./rr retry, not a fresh content submission."})
            return
        raw = (self.folder / "draft.json").read_bytes()
        with (self.folder / "submission.txt").open("xb") as stream:
            stream.write(raw)
        self.update(status="content_saved", saved_hashes={"submission.txt": digest(self.folder / "submission.txt")}, content_saved_at=now())
        self.build()

    def build(self):
        try:
            self.consistent()
            packet = json.loads((self.folder / "submission.txt").read_text(encoding="utf-8"))
            page = render(packet, (self.folder / "source.md").read_text(encoding="utf-8"))
            save(self.folder / "packet.json", packet)
            (self.folder / "report.html").write_text(page, encoding="utf-8")
            hashes = dict(self.receipt["saved_hashes"])
            hashes.update({name: digest(self.folder / name) for name in ["packet.json", "report.html"]})
            self.update(status="report_ready", saved_hashes=hashes, rendered_at=now(), failed_step=None, error=None)
        except Exception as error:
            self.failure("render", error)
            return
        self.check()

    def check(self):
        started = now()
        try:
            self.consistent()
            self.update(status="checking", failed_step="check")
            proc = subprocess.run([os.environ.get("REPORT_NODE_BIN", "node"), str(CHECKER), str(self.folder)], text=True, capture_output=True, timeout=32)
            self.command_attempt("check", proc)
            if proc.returncode:
                raise RuntimeError(proc.stderr.strip() or f"Checker exited {proc.returncode}")
            result = json.loads(proc.stdout)
            self.receipt["timings"]["machine_command_seconds"] = round((datetime.now(timezone.utc) - datetime.fromisoformat(started)).total_seconds(), 3)
            self.update(status="awaiting_review", review_directory=result["review_directory"], machine_status=result["machine_status"], machine_finished_at=now(), failed_step=None, error=None)
            self.request()
        except Exception as error:
            self.failure("check", error)

    def command_attempt(self, step, proc):
        attempt = self.folder / "attempts" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + "-" + step)
        attempt.mkdir(parents=True)
        (attempt / "stdout.txt").write_text(proc.stdout)
        (attempt / "stderr.txt").write_text(proc.stderr)
        save(attempt / "result.json", {"step": step, "returncode": proc.returncode, "at": now()})

    def request(self):
        review = Path(self.receipt["review_directory"])
        request = read(review / "review-request.json")
        request["finish_invocation"] = {"program": "./rr", "arguments": ["finish"], "input_file": "verdict.json"}
        emit({"status": self.receipt["status"], "machine_status": self.receipt["machine_status"], "report": str(self.folder / "report.html"), "review_request": request, "next": "View both images, write only submission to verdict.json, then ./rr finish. If the machine was incomplete, resolve the named tool problem and use ./rr retry before image review."})

    def finish(self, retry=False):
        try:
            self.consistent()
            if not self.receipt.get("review_directory"):
                raise ValueError("No machine review exists; use ./rr retry")
            review = Path(self.receipt["review_directory"])
            result = read(review / "receipt.json")
            if result["status"] != "awaiting_model_review":
                self.complete(result)
                return
            raw_path = self.folder / "last-review-submission.txt"
            if not retry:
                raw_path.write_bytes((self.folder / "verdict.json").read_bytes())
            raw = raw_path.read_text(encoding="utf-8")
            submitted = self.folder / "review-submissions" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + ".txt")
            submitted.parent.mkdir(exist_ok=True)
            submitted.write_text(raw, encoding="utf-8")
            self.update(failed_step="finish")
            proc = subprocess.run([os.environ.get("REPORT_NODE_BIN", "node"), str(CHECKER), "finish", str(review)], input=raw, text=True, capture_output=True, timeout=8)
            self.command_attempt("finish", proc)
            if proc.returncode:
                self.update(status="awaiting_review", failed_step="finish", error=proc.stderr.strip())
                emit({"status": "rejected", "error": proc.stderr.strip(), "next": "If the checklist needs correction, edit only verdict.json and run ./rr finish. To retry unchanged saved submission after a tool problem, use ./rr retry. Draft and failed review submission are preserved."})
                return
            self.complete(json.loads(proc.stdout))
        except Exception as error:
            self.failure("finish", error)

    def complete(self, result):
        self.receipt["timings"]["model_review_wall_seconds"] = result.get("model_review_wall_seconds")
        self.receipt["timings"]["total_wall_seconds"] = round((datetime.now(timezone.utc) - datetime.fromisoformat(self.receipt["started_at"])).total_seconds(), 3)
        self.update(status=result["status"], review=result, finished_at=now(), failed_step=None, error=None)
        self.status()

    def retry(self):
        step = self.receipt.get("failed_step")
        if step == "finish":
            self.finish(retry=True)
        elif step == "check":
            self.check()
        elif step == "render" or self.receipt["status"] == "content_saved":
            self.build()
        elif self.receipt["status"] == "awaiting_review":
            if self.receipt["machine_status"] == "incomplete":
                self.check()
            else:
                self.request()
        elif self.receipt["status"] == "report_ready":
            self.check()
        else:
            self.status()

    def status(self):
        self.consistent()
        emit({"status": self.receipt["status"], "producer": self.receipt["producer"], "report": str(self.folder / "report.html") if (self.folder / "report.html").exists() else None, "receipt": str(self.path), "machine_status": self.receipt.get("machine_status", "not_run"), "failed_step": self.receipt.get("failed_step"), "error": self.receipt.get("error"), "scope": "Three content checks and two first-section images only; PDF export is not print visual acceptance; no external fact checking or human acceptance."})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("init")
    create.add_argument("source", type=Path, help="UTF-8 report snapshot; preserve the original when extracting other formats")
    create.add_argument("--work", type=Path, required=True)
    create.add_argument("--producer-model", default="unknown", help="Actual model returned by dispatch, never an assumed model")
    create.add_argument("--producer-effort", default="unknown")
    create.add_argument("--producer-evidence", default="not supplied", help="Dispatch/tool evidence or a truthful unavailability note")
    for command in ["context", "submit", "retry", "finish", "status"]:
        sub.add_parser(command)
    args = parser.parse_args()
    try:
        if args.command == "init":
            init(args)
        else:
            getattr(Run(), args.command)()
    except Exception as error:
        emit({"status": "rejected", "error": str(error)})
        raise SystemExit(1)


if __name__ == "__main__":
    main()
