# Oh My Skills

[中文](README.md) | English

A personal collection of Codex Skills. Each Skill is an independent sibling directory under `skills/`. The three current Skills help make complex work clear before implementation, keep consequential stages within their agreed boundary, and explain conclusions plainly.

## Which Skill to use first

```text
The required change is still unclear
  → requirement-definition

The work is defined but each new concept must prove it is indispensable
  → first-principles-gate

An existing report needs a clearer explanation of conclusions, reasons, and limits
  → readable-report
```

They can be used in sequence: use `requirement-definition` to confirm the irreducible need, then use `first-principles-gate` to derive the smallest concept budget from the user outcome and freeze pass conditions. Neither replaces design, task decomposition, implementation, or release.

## Included Skills

### `requirement-definition`: establish what must actually change

**Core problem.** Once a requirement is mostly stated, clarification can still keep inventing edge cases or reopen answered branches in different words. “Keep clarifying” becomes an imagination contest with no convergent end.

This Skill models the need as a tree rooted in “who needs to change → current state → required result.” It applies a deletion test: if removing something leaves the root problem unchanged, it is a solution; if the need changes, it is irreducible core. Questions may come only from conflicts and gaps already present in the material. Each round asks one question that can still change the judgment; answered branches stay closed, and it converges as soon as the frontier is empty.

**How it differs from common requirement, PRD, or backlog Skills.**

- They often organize the user's first framing; this Skill tests whether that framing confuses a solution, cause, or value judgment with a requirement.
- They often produce a proposal, priorities, task list, or specification; this Skill stops at the root goal, irreducible core, confirmed boundaries, and material unresolved assumptions.
- They may aim to ask every useful question and keep adding imagined edge cases; this Skill does not invent branches outside the material, keeps one currently decisive question, and leaves answered branches closed.

Use it when real conflicts or gaps can still change the outcome, but discussion has begun to repeat or expand, or the work needs a reason to exist before design begins. Do not use it for a small reversible change whose goal and boundary are already clear.

### `first-principles-gate`: make complex designs prove every added concept

**Core problem.** A complex task can keep going because it was planned, partly completed, or once approved—not because the next work can still be derived from the original requirement and current facts. Sunk cost, inertia, and self-justification can replace a present justification for continuing.

This Skill separates user outcomes, hard constraints, current facts, and candidate mechanisms; freezes the audit object and the pre-feature baseline; and counts concepts by the independent distinctions a future maintainer must remember. A design claiming `N` concepts must build a one-concept-at-a-time proof from zero and then remove each concept from the complete design. A deterministic validator checks count conservation, ladder shape, requirement coverage, evidence references, and baseline provenance. A lower-cost Luna or Terra challenger may independently propose a smaller budget, but there is no vote: the more complex design must answer with a current, cited failure. Historical `PASS`, committed code, and passing tests cannot launder feature-created complexity into a zero-cost baseline. The Skill remains explicit-only through `$first-principles-gate`.

User-facing output is concise by default; full evidence stays in working materials. Before-addition and full-design deletion conditions are checked separately. Each proof has one body, and follow-up reviews update only entries affected by changed premises or responsibilities. Lower-budget proposals are compared by actual behavior and maintenance duties before counts, so renaming or merging descriptions does not count as simplification.

The validator now requires an explicit baseline and checks failure-proof bodies or resolvable references within the budget. An empty baseline cannot support baseline coverage; empty bodies, broken references, and reference cycles are rejected. Older budgets containing only IDs or invalid references need repair. Structural `PASS` does not establish a sound argument. `STOP` applies only to the current object proven unnecessary; an unavailable auditor pauses dependent steps without issuing a new verdict. The budget validator has 31 regression tests; these checks do not establish overall efficiency gains.

**How it differs from common code reviews, quality gates, and checklists.**

- They usually test fixed engineering criteria; this Skill first asks whether every added long-lived concept has a right to exist.
- They can use “more rigorous” as sufficient justification; this Skill makes the more complex design prove why a smaller one fails.
- They often measure code or terminology; this Skill measures independent maintenance distinctions and tests them with a `0→N` ladder, delete-one proofs, and a lower-budget challenger.
- They can re-review the whole task each round; this Skill keeps one logical gate and performs bounded closure against a frozen first-round list.

Use it for complex staged work whose next investment needs to be shown still worthwhile; formal objects or consequential external actions make the gate especially useful. Do not use it for simple reversible work, and do not treat it as an automated lock that decides for the executor.

### `readable-report`: turn an existing report into an understandable reading edition

Preserve the original and create a separate reading edition that explains conclusions, reasons, and limits without adding research or turning uncertainty into certainty. By default, a single Luna / medium producer writes the explanation; bundled scripts assemble standalone HTML and run fixed checks, followed by three content self-checks and a review of two screenshots.

Use it to improve report readability, reorganize long reports, or create a visual reading edition. It is not for new research, fact verification, or a few-sentence summary. Short or text-only rewrites can be delivered as Markdown.

Default machine checks require Python, Node with built-in WebSocket support, and Chrome. Missing tools are recorded as incomplete and are not installed automatically. `passed_in_scope` covers only the specified self-checks and screenshots, not full visual review, external fact verification, or user acceptance.

## Install

Clone the repository:

```bash
git clone https://github.com/HYBB-rash/oh-my-skills.git
```

Copy the needed Skills into the default Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R oh-my-skills/skills/requirement-definition "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R oh-my-skills/skills/first-principles-gate "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R oh-my-skills/skills/readable-report "${CODEX_HOME:-$HOME/.codex}/skills/"
```

For a different Skill root, copy the corresponding `skills/<skill-name>` directory there.

## Invocation examples

```text
Use $requirement-definition to identify the irreducible requirement behind this proposal.

Use $first-principles-gate to derive the smallest concept budget from the user outcome and block unsupported persistent complexity.

Use $readable-report to create a readable edition of this report, preserving evidence and limits.
```

## Repository layout

```text
.
├── README.md                 # Chinese default landing page
├── README.en.md              # English documentation
├── CHANGELOG.md
├── LICENSE
├── VERSION
└── skills/
    ├── first-principles-gate/
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   ├── scripts/validate_complexity_budget.py
    │   └── tests/test_complexity_budget.py
    ├── readable-report/
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   ├── assets/
    │   ├── references/
    │   └── scripts/
    └── requirement-definition/
        ├── SKILL.md
        └── agents/openai.yaml
```

## Versioning and license

The project follows [Semantic Versioning](https://semver.org/); notable changes appear in [CHANGELOG.md](CHANGELOG.md).

[MIT](LICENSE)
