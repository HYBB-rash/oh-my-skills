#!/usr/bin/env python3
import json
import sys
from pathlib import Path


ALLOWED_EVIDENCE_KINDS = {
    "baseline_fact",
    "user_result",
    "hard_constraint",
    "current_fact",
    "verified_failure",
}


def non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def duplicate_ids(values: list[str]) -> bool:
    return len(values) != len(set(values))


def validate_failure(
    failure: object,
    path: str,
    requirement_ids: set[str],
    evidence_ids: set[str],
    errors: list[dict[str, str]],
) -> None:
    if not isinstance(failure, dict):
        errors.append({"code": "E_FAILURE_PROOF", "path": path})
        return

    requirement_id = failure.get("requirement_id")
    if requirement_id not in requirement_ids:
        errors.append({"code": "E_REQUIREMENT_REFERENCE", "path": f"{path}.requirement_id"})

    cited = failure.get("evidence_ids")
    if not isinstance(cited, list) or not cited or not all(non_empty_string(item) for item in cited):
        errors.append({"code": "E_EVIDENCE_REFERENCE", "path": f"{path}.evidence_ids"})
    elif any(item not in evidence_ids for item in cited):
        errors.append({"code": "E_EVIDENCE_REFERENCE", "path": f"{path}.evidence_ids"})


def validate_budget(data: object) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return [{"code": "E_BUDGET_ROOT", "path": "$"}]

    scope = data.get("audit_scope")
    baseline = scope.get("baseline", []) if isinstance(scope, dict) else []
    if (
        not isinstance(scope, dict)
        or not non_empty_string(scope.get("object"))
        or scope.get("mode") not in {"whole_feature", "next_delta"}
        or not isinstance(baseline, list)
        or any(
            not isinstance(item, dict)
            or not non_empty_string(item.get("capability"))
            or not isinstance(item.get("evidence_ids"), list)
            or not item.get("evidence_ids")
            or not all(non_empty_string(evidence_id) for evidence_id in item.get("evidence_ids", []))
            for item in baseline
        )
    ):
        errors.append({"code": "E_AUDIT_SCOPE", "path": "audit_scope"})

    requirements = data.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        requirements = []
        errors.append({"code": "E_REQUIREMENTS", "path": "requirements"})
    requirement_ids = [
        item.get("id")
        for item in requirements
        if isinstance(item, dict) and non_empty_string(item.get("id")) and non_empty_string(item.get("text"))
    ]
    if len(requirement_ids) != len(requirements) or duplicate_ids(requirement_ids):
        errors.append({"code": "E_REQUIREMENTS", "path": "requirements"})
    requirement_id_set = set(requirement_ids)

    evidence = data.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        evidence = []
        errors.append({"code": "E_EVIDENCE", "path": "evidence"})
    evidence_ids: list[str] = []
    for index, item in enumerate(evidence):
        if not isinstance(item, dict) or not non_empty_string(item.get("id")) or not non_empty_string(item.get("text")):
            errors.append({"code": "E_EVIDENCE", "path": f"evidence[{index}]"})
            continue
        evidence_ids.append(item["id"])
        if item.get("kind") not in ALLOWED_EVIDENCE_KINDS:
            errors.append({"code": "E_EVIDENCE_KIND", "path": f"evidence[{index}].kind"})
    if duplicate_ids(evidence_ids):
        errors.append({"code": "E_EVIDENCE", "path": "evidence"})
    evidence_id_set = set(evidence_ids)
    evidence_kind_by_id = {
        item["id"]: item.get("kind")
        for item in evidence
        if isinstance(item, dict) and non_empty_string(item.get("id"))
    }
    if isinstance(baseline, list):
        for index, item in enumerate(baseline):
            if not isinstance(item, dict) or not isinstance(item.get("evidence_ids"), list):
                continue
            if any(evidence_kind_by_id.get(evidence_id) != "baseline_fact" for evidence_id in item["evidence_ids"]):
                errors.append({"code": "E_BASELINE_PROVENANCE", "path": f"audit_scope.baseline[{index}].evidence_ids"})

    concepts = data.get("concepts")
    if not isinstance(concepts, list):
        concepts = []
        errors.append({"code": "E_CONCEPTS", "path": "concepts"})
    concept_ids = [
        item.get("id")
        for item in concepts
        if isinstance(item, dict) and non_empty_string(item.get("id")) and non_empty_string(item.get("definition"))
    ]
    expected_concept_ids = [f"C{index}" for index in range(1, len(concepts) + 1)]
    if len(concept_ids) != len(concepts) or concept_ids != expected_concept_ids:
        errors.append({"code": "E_CONCEPT_IDS", "path": "concepts"})
    concept_id_set = set(concept_ids)

    claimed_count = data.get("claimed_count")
    if isinstance(claimed_count, bool) or not isinstance(claimed_count, int) or claimed_count != len(concepts):
        errors.append({"code": "E_COUNT_MISMATCH", "path": "claimed_count"})

    coverage = data.get("coverage")
    if not isinstance(coverage, list):
        coverage = []
    covered_requirements: list[str] = []
    for index, item in enumerate(coverage):
        if not isinstance(item, dict):
            errors.append({"code": "E_REQUIREMENT_COVERAGE", "path": f"coverage[{index}]"})
            continue
        requirement_id = item.get("requirement_id")
        satisfied_by = item.get("satisfied_by")
        if requirement_id not in requirement_id_set:
            errors.append({"code": "E_REQUIREMENT_COVERAGE", "path": f"coverage[{index}].requirement_id"})
        else:
            covered_requirements.append(requirement_id)
        if (
            not isinstance(satisfied_by, list)
            or not satisfied_by
            or any(value != "baseline" and value not in concept_id_set for value in satisfied_by)
        ):
            errors.append({"code": "E_REQUIREMENT_COVERAGE", "path": f"coverage[{index}].satisfied_by"})
    if set(covered_requirements) != requirement_id_set or duplicate_ids(covered_requirements):
        errors.append({"code": "E_REQUIREMENT_COVERAGE", "path": "coverage"})

    ladder = data.get("ladder")
    if not isinstance(ladder, list) or len(ladder) != len(concepts) + 1:
        errors.append({"code": "E_LADDER_LENGTH", "path": "ladder"})
    else:
        for index, step in enumerate(ladder):
            expected_prefix = expected_concept_ids[:index]
            if not isinstance(step, dict) or step.get("step") != index or step.get("concept_ids") != expected_prefix:
                errors.append({"code": "E_LADDER_STEP", "path": f"ladder[{index}]"})
                continue
            if index == 0:
                if "added" in step or "failure_before" in step:
                    errors.append({"code": "E_LADDER_STEP", "path": "ladder[0]"})
                continue
            if step.get("added") != expected_concept_ids[index - 1]:
                errors.append({"code": "E_LADDER_STEP", "path": f"ladder[{index}].added"})
            validate_failure(
                step.get("failure_before"),
                f"ladder[{index}].failure_before",
                requirement_id_set,
                evidence_id_set,
                errors,
            )

    delete_one = data.get("delete_one")
    if not isinstance(delete_one, list):
        delete_one = []
    deleted_ids = [item.get("concept_id") for item in delete_one if isinstance(item, dict)]
    if len(delete_one) != len(concepts) or deleted_ids != expected_concept_ids:
        errors.append({"code": "E_DELETE_ONE_COVERAGE", "path": "delete_one"})
    for index, item in enumerate(delete_one):
        if not isinstance(item, dict):
            continue
        validate_failure(
            item.get("failure"),
            f"delete_one[{index}].failure",
            requirement_id_set,
            evidence_id_set,
            errors,
        )

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        payload = {"status": "REVISE", "concept_count": 0, "errors": [{"code": "E_USAGE", "path": "$"}]}
        print(json.dumps(payload, ensure_ascii=False))
        return 1

    try:
        data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        payload = {"status": "REVISE", "concept_count": 0, "errors": [{"code": "E_INPUT_JSON", "path": "$"}]}
        print(json.dumps(payload, ensure_ascii=False))
        return 1

    errors = validate_budget(data)
    concept_count = len(data.get("concepts", [])) if isinstance(data, dict) and isinstance(data.get("concepts"), list) else 0
    payload = {
        "status": "PASS" if not errors else "REVISE",
        "concept_count": concept_count,
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
