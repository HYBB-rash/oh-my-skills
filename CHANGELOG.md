# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- Synced the 2026-09-07 `first-principles-gate`: concise default conclusions, single-body proof reuse, full-design delete-one checks, and follow-up updates limited to changed premises or responsibilities.
- Compare challengers by actual behavior and maintenance responsibilities before concept counts.

- Reworked `first-principles-gate` around a frozen pre-feature baseline, atomic concept budgets, `0→N` necessity ladders, delete-one proofs, and independent lower-budget challengers.

### Added

- Added deterministic validation for concept-count conservation, requirement coverage, evidence references, and baseline provenance, with rule-derived regression tests.

### Fixed

- Require an explicit baseline; reject coverage that relies on an empty baseline.
- Require failure-proof text or valid local proof references; reject missing bodies, broken targets, metadata-only targets, and reference cycles. Older ID-only budgets must be repaired. Structural validation still does not judge semantic validity.
- Limit `STOP` to the object shown unnecessary, and pause only audit-dependent steps when the auditor is unavailable without inventing a new verdict.

### Removed

- Removed the unused `skill-contract.json` and text-rule test; retained and expanded the budget validator's regression suite to 31 tests.

## [0.4.0] - 2026-08-31

### Added

- Added `plain-chinese` for concise Chinese explanations that lead with the conclusion and distinguish facts, inference, and uncertainty.

## [0.3.0] - 2026-08-31

### Added

- Added the explicitly invoked `first-principles-gate` Skill for independent stage audits, frozen pass conditions, and bounded checkpoint closure.

## [0.2.0] - 2026-08-31

### Changed

- Replaced `progressive-todo-tree` with `requirement-definition`.
- Reframed the Skill around a requirement tree, deletion test, one decisive question per round, and explicit convergence at the requirement boundary.
- Updated installation, invocation, and repository-layout documentation for the new Skill path.

## [0.1.0] - 2026-08-13

### Added

- Persistent TODO state with a clean human-facing tree and compact Agent handoff context.
- First-principles reconstruction of outcomes, facts, constraints, and assumptions.
- Relative `1000 / 100 / 10` budget compression before major investment.
- Route review, explicit pause and recovery behavior, and user-confirmed root changes.
- Per-branch archival for closed top-level branches.
- English and Simplified Chinese project documentation.

[0.1.0]: https://github.com/HYBB-rash/oh-my-skills/releases/tag/v0.1.0
[0.2.0]: https://github.com/HYBB-rash/oh-my-skills/releases/tag/v0.2.0
[0.3.0]: https://github.com/HYBB-rash/oh-my-skills/releases/tag/v0.3.0
[0.4.0]: https://github.com/HYBB-rash/oh-my-skills/releases/tag/v0.4.0
