# Oh My Skills

[中文](README.md) | English

A personal collection of Codex Skills. Each Skill is an independent sibling directory under `skills/`. The two current Skills help make complex work clear before implementation and keep consequential stages within their agreed boundary.

## Which Skill to use first

```text
The required change is still unclear
  → requirement-definition

The work is defined but a complex stage needs a bounded, independent checkpoint
  → first-principles-gate
```

They can be used in sequence: use `requirement-definition` to confirm the irreducible need, then use `first-principles-gate` to freeze pass conditions for a consequential later stage. Neither replaces design, task decomposition, implementation, or release.

## Included Skills

### `requirement-definition`: establish what must actually change

**Core problem.** A discussion often mixes pains, candidate solutions, preferences, constraints, and guesses. Teams can mistake the first proposed solution for the requirement and move directly into design or planning.

This Skill models the need as a tree rooted in “who needs to change → current state → required result.” It applies a deletion test: if removing something leaves the root problem unchanged, it is a solution; if the need changes, it is irreducible core. Each round asks only the question that can still change the root goal, value order, unacceptable outcome, or boundary; it converges only when that frontier is empty.

**How it differs from common requirement, PRD, or backlog Skills.**

- They often organize the user's first framing; this Skill tests whether that framing confuses a solution, cause, or value judgment with a requirement.
- They often produce a proposal, priorities, task list, or specification; this Skill stops at the root goal, irreducible core, confirmed boundaries, and material unresolved assumptions.
- They may aim to ask every useful question; this Skill keeps one currently decisive question and leaves answered branches closed.

Use it when the need is ambiguous, solutions compete, goals conflict, or the work needs a reason to exist before design begins. Do not use it for a small reversible change whose goal and boundary are already clear.

### `first-principles-gate`: close a complex stage within its evidence boundary

**Core problem.** Even with a plan, complex work can expand during execution, cycle through new auditors, treat “more rigor” as a reason for endless rework, or cross an external-action boundary without a confirmed condition.

This Skill creates one logical stage gate. A fresh independent auditor first blind-reviews the original requirements and current facts, then freezes observable pass conditions. Only decisive new evidence reopens the smallest relevant condition. At the next decision boundary, the same auditor performs bounded closure and returns `PASS`, `REVISE`, or `STOP`. It is explicit-only: invoke `$first-principles-gate`; it does not activate by itself.

**How it differs from common code reviews, quality gates, and checklists.**

- They usually test fixed engineering criteria; this Skill first tests whether the stage is necessary and whether it crosses its agreed authority, formal-object, or external-action boundary.
- They can re-review the whole task each round; this Skill freezes scope and revisits only conditions genuinely reopened by new evidence.
- They can let an abstract wish for rigor block progress; this Skill permits `REVISE` only for evidenced necessity conflicts, decisive missing facts, or serious hard-to-recover risks. Other concerns remain non-blocking notes.

Use it for complex staged work with formal objects or consequential external actions that needs independent counterargument and a clear conclusion. Do not use it for simple reversible work, and do not treat it as an automated lock that decides for the executor.

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
```

For a different Skill root, copy the corresponding `skills/<skill-name>` directory there.

## Invocation examples

```text
Use $requirement-definition to identify the irreducible requirement behind this proposal.

Use $first-principles-gate to establish a stage gate for this complex task.
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
    │   └── agents/openai.yaml
    └── requirement-definition/
        ├── SKILL.md
        └── agents/openai.yaml
```

## Versioning and license

The project follows [Semantic Versioning](https://semver.org/); notable changes appear in [CHANGELOG.md](CHANGELOG.md).

[MIT](LICENSE)
