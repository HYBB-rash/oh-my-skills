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
                "failure_before": {
                    "requirement_id": "R1", "evidence_ids": ["E1"],
                    "proof": "Telegram delivery alone cannot observe completion on all three surfaces.",
                },
            },
            {
                "step": 2,
                "concept_ids": ["C1", "C2"],
                "added": "C2",
                "failure_before": {
                    "requirement_id": "R2", "evidence_ids": ["E2"],
                    "proof": "Observation without a completeness decision can report success with an unknown surface.",
                },
            },
        ],
        "delete_one": [
            {
                "concept_id": "C1",
                "failure": {
                    "requirement_id": "R1", "evidence_ids": ["E1"],
                    "proof": "A completeness decision without observation cannot establish all three surfaces completed.",
                },
            },
            {
                "concept_id": "C2",
                "failure": {
                    "requirement_id": "R2", "evidence_ids": ["E2"],
                    "proof": "Keeping observation but deleting the decision allows an unknown surface to count as complete.",
                },
            },
        ],
    }


def failure_records(budget: dict) -> list[dict]:
    return [step["failure_before"] for step in budget["ladder"][1:]] + [
        item["failure"] for item in budget["delete_one"]
    ]


def valid_reused_budget() -> dict:
    budget = valid_budget()
    for index, concept in enumerate(budget["concepts"]):
        before = budget["ladder"][index + 1]["failure_before"]
        deletion = budget["delete_one"][index]["failure"]
        concept["necessity"] = {
            "before": before.pop("proof"),
            "delete_from_full": deletion.pop("proof"),
        }
        before["proof_ref"] = f"{concept['id']}.necessity.before"
        deletion["proof_ref"] = f"{concept['id']}.necessity.delete_from_full"
    return budget


def valid_zero_concept_budget() -> dict:
    budget = valid_budget()
    budget["requirements"] = [{"id": "R1", "text": "Keep existing Telegram delivery available."}]
    budget["evidence"] = [
        budget["evidence"][0],
        {"id": "E1", "kind": "user_result", "text": "The user only needs existing Telegram delivery."},
    ]
    budget["claimed_count"] = 0
    budget["concepts"] = []
    budget["coverage"] = [{"requirement_id": "R1", "satisfied_by": ["baseline"]}]
    budget["ladder"] = [{"step": 0, "concept_ids": []}]
    budget["delete_one"] = []
    return budget


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

    def assert_pass(self, budget: dict) -> None:
        result, payload = self.run_validator(budget)
        self.assertEqual(result.returncode, 0, result.stderr or payload)
        self.assertEqual(payload, {"status": "PASS", "concept_count": len(budget["concepts"]), "errors": []})

    def test_accepts_existing_direct_body_field_spellings(self) -> None:
        for field in ("proof", "explanation", "reasoning", "argument", "path", "text"):
            with self.subTest(field=field):
                budget = valid_budget()
                for failure in failure_records(budget):
                    failure[field] = failure.pop("proof")
                self.assert_pass(budget)

    def test_accepts_resolved_before_and_delete_proof_references(self) -> None:
        self.assert_pass(valid_reused_budget())

    def test_accepts_existing_reference_field_and_path_spellings(self) -> None:
        for field in ("proof_ref", "proof_reference"):
            for prefix in ("", "concepts."):
                with self.subTest(field=field, prefix=prefix):
                    budget = valid_reused_budget()
                    for concept in budget["concepts"]:
                        concept["necessity_proof"] = concept.pop("necessity")
                    for failure in failure_records(budget):
                        failure[field] = prefix + failure.pop("proof_ref").replace(".necessity.", ".necessity_proof.")
                    self.assert_pass(budget)

    def test_accepts_a_string_or_body_object_as_a_shared_proof(self) -> None:
        for as_object in (False, True):
            with self.subTest(as_object=as_object):
                budget = valid_reused_budget()
                for concept in budget["concepts"]:
                    body = "With this responsibility absent, the other retained responsibilities cannot provide the missing behavior."
                    concept["necessity"] = {"reachable_failure_without": body} if as_object else body
                for failure in failure_records(budget):
                    failure["proof_ref"] = failure["proof_ref"].rsplit(".", 1)[0]
                self.assert_pass(budget)

    def test_accepts_an_acyclic_explicit_reference_chain(self) -> None:
        budget = valid_reused_budget()
        necessity = budget["concepts"][0]["necessity"]
        necessity["failure_path"] = necessity["before"]
        necessity["before"] = {"proof_ref": "concepts.C1.necessity.failure_path"}
        self.assert_pass(budget)

    def test_requires_a_body_for_every_ladder_and_deletion_failure(self) -> None:
        for index in range(4):
            with self.subTest(index=index):
                budget = valid_budget()
                del failure_records(budget)[index]["proof"]
                self.assert_revise(budget, "E_FAILURE_PROOF")

    def test_rejects_blank_or_non_string_direct_bodies(self) -> None:
        for value in ("", " \n\t", None, [], {}, 123):
            with self.subTest(value=value):
                budget = valid_budget()
                budget["ladder"][1]["failure_before"]["proof"] = value
                self.assert_revise(budget, "E_FAILURE_PROOF")

    def test_rejects_identifiers_or_a_bare_reference_as_body_text(self) -> None:
        for value in ("R1", "E1", "C1", "R404", "R1 / E1", "[R1], (E1).", "...",
                      "C1.necessity.before", "concepts.C1.necessity", "R1.text", "E404.text",
                      "C404.necessity.before", "concepts.C404.necessity",
                      "见 C1", "参考：C1.necessity.before。", "引用 R1 / E1", "See C1.necessity",
                      "refer to C1.necessity.before"):
            with self.subTest(value=value):
                budget = valid_budget()
                budget["ladder"][1]["failure_before"]["proof"] = value
                self.assert_revise(budget, "E_FAILURE_PROOF")

    def test_accepts_prose_with_dots_outside_reference_roots(self) -> None:
        for body in ("输入为空.校验器拒绝输出", "缺少观察.无法确认所有渠道完成"):
            for reused in (False, True):
                with self.subTest(body=body, reused=reused):
                    budget = valid_reused_budget() if reused else valid_budget()
                    if reused:
                        budget["concepts"][0]["necessity"]["before"] = body
                    else:
                        budget["ladder"][1]["failure_before"]["proof"] = body
                    self.assert_pass(budget)

    def test_accepts_existing_prose_that_also_mentions_a_reference(self) -> None:
        budget = valid_budget()
        budget["ladder"][1]["failure_before"]["proof"] = "见 C1.necessity；其他已加入责任不拥有该独立边界。"
        # Embedded natural-language references are not resolved mechanically.
        self.assert_pass(budget)

    def test_rejects_missing_or_out_of_scope_reference_paths(self) -> None:
        for ref in ("", " ", None, 123, "C404.necessity", "R1.text", "C1.definition",
                    "C1.necessity.missing", "C1.necessity.before.extra", "concepts[0].necessity",
                    "../proof.json", "https://example.com/proof"):
            with self.subTest(ref=ref):
                budget = valid_reused_budget()
                budget["ladder"][1]["failure_before"]["proof_ref"] = ref
                self.assert_revise(budget, "E_PROOF_REFERENCE")

    def test_rejects_empty_targets_and_metadata_only_objects(self) -> None:
        for value in ("", " \n\t", "R1 E1", None, [], 123, {}, {"proof": "E1"},
                      {"reachable_failure_without": " "},
                      {"id": "N1", "requirement_ids": ["R1"], "evidence_ids": ["E1"],
                       "condition": "This is an applicability condition, not a failure body."}):
            with self.subTest(value=value):
                budget = valid_reused_budget()
                budget["concepts"][0]["necessity"] = value
                for failure in failure_records(budget):
                    if failure["proof_ref"].startswith("C1."):
                        failure["proof_ref"] = "C1.necessity"
                self.assert_revise(budget, "E_PROOF_REFERENCE_TARGET")

    def test_rejects_a_reference_to_a_metadata_string(self) -> None:
        budget = valid_reused_budget()
        budget["concepts"][0]["necessity"]["condition"] = "Only applies when all surfaces are requested."
        budget["ladder"][1]["failure_before"]["proof_ref"] = "C1.necessity.condition"
        self.assert_revise(budget, "E_PROOF_REFERENCE")

    def test_does_not_treat_an_id_value_as_a_path_key(self) -> None:
        budget = valid_reused_budget()
        budget["concepts"][0]["necessity"]["id"] = "N1"
        budget["ladder"][1]["failure_before"]["proof_ref"] = "C1.necessity.N1"
        self.assert_revise(budget, "E_PROOF_REFERENCE")

    def test_rejects_reference_cycles_even_with_a_body_on_the_cycle(self) -> None:
        for cycle_length in (1, 2):
            with self.subTest(cycle_length=cycle_length):
                budget = valid_reused_budget()
                budget["ladder"][1]["failure_before"]["proof_ref"] = "C1.necessity"
                budget["concepts"][0]["necessity"]["proof_ref"] = f"C{cycle_length}.necessity"
                if cycle_length == 2:
                    budget["concepts"][1]["necessity"]["proof_ref"] = "concepts.C1.necessity"
                self.assert_revise(budget, "E_PROOF_REFERENCE_CYCLE")

    def test_rejects_an_explicit_bad_reference_alongside_valid_direct_prose(self) -> None:
        budget = valid_budget()
        budget["ladder"][1]["failure_before"]["proof_ref"] = "C404.necessity"
        self.assert_revise(budget, "E_PROOF_REFERENCE")

    def test_structure_pass_does_not_establish_semantic_validity(self) -> None:
        budget = valid_budget()
        for failure in failure_records(budget):
            failure["proof"] = "Deleting this concept still satisfies every requirement, so this concept is necessary."
        # Intentionally unsound prose remains structurally valid: an auditor,
        # not keyword matching, must judge the argument and reuse conditions.
        self.assert_pass(budget)

    def test_accepts_a_complete_two_concept_proof(self) -> None:
        result, payload = self.run_validator(valid_budget())
        self.assertEqual(result.returncode, 0)
        self.assertEqual(payload, {"status": "PASS", "concept_count": 2, "errors": []})

    def test_accepts_zero_concepts_supported_by_a_documented_baseline(self) -> None:
        result, payload = self.run_validator(valid_zero_concept_budget())
        self.assertEqual(result.returncode, 0)
        self.assertEqual(payload, {"status": "PASS", "concept_count": 0, "errors": []})

    def test_rejects_zero_concepts_claiming_an_empty_or_missing_baseline(self) -> None:
        for missing in (False, True):
            with self.subTest(missing=missing):
                budget = valid_zero_concept_budget()
                if missing:
                    del budget["audit_scope"]["baseline"]
                else:
                    budget["audit_scope"]["baseline"] = []
                self.assert_revise(budget, "E_REQUIREMENT_COVERAGE")

    def test_rejects_an_empty_baseline_in_mixed_coverage(self) -> None:
        budget = valid_budget()
        budget["audit_scope"]["baseline"] = []
        budget["coverage"][0]["satisfied_by"] = ["baseline", "C1"]
        self.assert_revise(budget, "E_REQUIREMENT_COVERAGE")

    def test_accepts_an_empty_baseline_when_concepts_cover_all_requirements(self) -> None:
        budget = valid_budget()
        budget["audit_scope"]["baseline"] = []
        result, payload = self.run_validator(budget)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(payload, {"status": "PASS", "concept_count": 2, "errors": []})

    def test_requires_an_explicit_baseline_declaration(self) -> None:
        budget = valid_budget()
        del budget["audit_scope"]["baseline"]
        self.assert_revise(budget, "E_AUDIT_SCOPE")

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
