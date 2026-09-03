import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_complexity_budget.py"


def valid_budget() -> dict:
    return {
        "audit_scope": {
            "object": "Personal Feed current feature",
            "mode": "whole_feature",
            "baseline": [
                {"capability": "Existing Telegram delivery", "evidence_ids": ["E0"]}
            ],
        },
        "requirements": [
            {"id": "R1", "text": "All three surfaces must complete."},
            {"id": "R2", "text": "Any unknown surface makes the request incomplete."},
        ],
        "evidence": [
            {"id": "E0", "kind": "baseline_fact", "text": "Telegram delivery existed before this feature."},
            {"id": "E1", "kind": "user_result", "text": "The user requested all three surfaces."},
            {"id": "E2", "kind": "hard_constraint", "text": "Unknown means INCOMPLETE."},
        ],
        "claimed_count": 2,
        "concepts": [
            {"id": "C1", "definition": "One request-scoped three-surface observation."},
            {"id": "C2", "definition": "One fail-closed completeness decision."},
        ],
        "coverage": [
            {"requirement_id": "R1", "satisfied_by": ["C1"]},
            {"requirement_id": "R2", "satisfied_by": ["C2"]},
        ],
        "ladder": [
            {"step": 0, "concept_ids": []},
            {
                "step": 1,
                "concept_ids": ["C1"],
                "added": "C1",
                "failure_before": {"requirement_id": "R1", "evidence_ids": ["E1"]},
            },
            {
                "step": 2,
                "concept_ids": ["C1", "C2"],
                "added": "C2",
                "failure_before": {"requirement_id": "R2", "evidence_ids": ["E2"]},
            },
        ],
        "delete_one": [
            {
                "concept_id": "C1",
                "failure": {"requirement_id": "R1", "evidence_ids": ["E1"]},
            },
            {
                "concept_id": "C2",
                "failure": {"requirement_id": "R2", "evidence_ids": ["E2"]},
            },
        ],
    }


class ComplexityBudgetValidatorTests(unittest.TestCase):
    def run_validator(self, budget: dict) -> tuple[subprocess.CompletedProcess[str], dict]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "budget.json"
            path.write_text(json.dumps(budget, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run(
                ["python3", str(VALIDATOR), str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        payload = json.loads(result.stdout)
        return result, payload

    def assert_revise(self, budget: dict, expected_code: str) -> None:
        result, payload = self.run_validator(budget)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(payload["status"], "REVISE")
        self.assertIn(expected_code, {error["code"] for error in payload["errors"]})

    def test_accepts_a_complete_two_concept_proof(self) -> None:
        result, payload = self.run_validator(valid_budget())
        self.assertEqual(result.returncode, 0)
        self.assertEqual(payload, {"status": "PASS", "concept_count": 2, "errors": []})

    def test_rejects_a_claimed_count_that_hides_extra_concepts(self) -> None:
        budget = valid_budget()
        budget["claimed_count"] = 1
        self.assert_revise(budget, "E_COUNT_MISMATCH")

    def test_rejects_a_ladder_step_that_adds_more_than_one_concept(self) -> None:
        budget = valid_budget()
        budget["ladder"][1]["concept_ids"] = ["C1", "C2"]
        self.assert_revise(budget, "E_LADDER_STEP")

    def test_rejects_a_concept_without_a_delete_one_proof(self) -> None:
        budget = valid_budget()
        budget["delete_one"] = budget["delete_one"][:1]
        self.assert_revise(budget, "E_DELETE_ONE_COVERAGE")

    def test_rejects_unknown_evidence_as_a_necessity_proof(self) -> None:
        budget = valid_budget()
        budget["evidence"][0]["kind"] = "unknown"
        self.assert_revise(budget, "E_EVIDENCE_KIND")

    def test_rejects_a_failure_that_cites_nonexistent_evidence(self) -> None:
        budget = valid_budget()
        budget["delete_one"][0]["failure"]["evidence_ids"] = ["E404"]
        self.assert_revise(budget, "E_EVIDENCE_REFERENCE")

    def test_rejects_an_unmapped_requirement(self) -> None:
        budget = valid_budget()
        budget["coverage"] = budget["coverage"][:1]
        self.assert_revise(budget, "E_REQUIREMENT_COVERAGE")

    def test_rejects_non_atomic_concept_ids(self) -> None:
        budget = valid_budget()
        budget["concepts"][1]["id"] = "C4"
        self.assert_revise(budget, "E_CONCEPT_IDS")

    def test_rejects_a_current_fact_laundered_into_the_baseline(self) -> None:
        budget = valid_budget()
        budget["audit_scope"]["baseline"][0]["evidence_ids"] = ["E1"]
        self.assert_revise(budget, "E_BASELINE_PROVENANCE")


if __name__ == "__main__":
    unittest.main()
