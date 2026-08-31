# Oh My Skills

[中文](README.md) | English

A personal collection of Codex Skills. Each Skill is an independent sibling directory under `skills/`. The three current Skills help make complex work clear before implementation, keep consequential stages within their agreed boundary, and explain conclusions plainly.

## Which Skill to use first

```text
The required change is still unclear
  → requirement-definition

The work is defined but a complex stage needs a bounded, independent checkpoint
  → first-principles-gate

The conclusion is known but must be stated plainly with evidence and uncertainty visible
  → plain-chinese
```

They can be used in sequence: use `requirement-definition` to confirm the irreducible need, then use `first-principles-gate` to freeze pass conditions for a consequential later stage. Neither replaces design, task decomposition, implementation, or release.

## Included Skills

### `requirement-definition`: establish what must actually change

**Core problem.** Once a requirement is mostly stated, clarification can still keep inventing edge cases or reopen answered branches in different words. “Keep clarifying” becomes an imagination contest with no convergent end.

This Skill models the need as a tree rooted in “who needs to change → current state → required result.” It applies a deletion test: if removing something leaves the root problem unchanged, it is a solution; if the need changes, it is irreducible core. Questions may come only from conflicts and gaps already present in the material. Each round asks one question that can still change the judgment; answered branches stay closed, and it converges as soon as the frontier is empty.

**How it differs from common requirement, PRD, or backlog Skills.**

- They often organize the user's first framing; this Skill tests whether that framing confuses a solution, cause, or value judgment with a requirement.
- They often produce a proposal, priorities, task list, or specification; this Skill stops at the root goal, irreducible core, confirmed boundaries, and material unresolved assumptions.
- They may aim to ask every useful question and keep adding imagined edge cases; this Skill does not invent branches outside the material, keeps one currently decisive question, and leaves answered branches closed.

Use it when real conflicts or gaps can still change the outcome, but discussion has begun to repeat or expand, or the work needs a reason to exist before design begins. Do not use it for a small reversible change whose goal and boundary are already clear.

### `first-principles-gate`: close a complex stage within its evidence boundary

**Core problem.** A complex task can keep going because it was planned, partly completed, or once approved—not because the next work can still be derived from the original requirement and current facts. Sunk cost, inertia, and self-justification can replace a present justification for continuing.

This Skill creates one logical stage gate. The executor first shows why the current plan, stage, and artifacts still follow from the original requirement and current facts. Before seeing the execution result, a fresh independent auditor blind-reviews the evidence and actively looks for a supported counterexample, then freezes observable pass conditions. Only decisive new evidence reopens the smallest relevant condition. At the next decision boundary, the same auditor performs bounded closure and returns `PASS`, `REVISE`, or `STOP`. A historical `PASS` is not a permanent credential. It is explicit-only: invoke `$first-principles-gate`; it does not activate by itself.

**How it differs from common code reviews, quality gates, and checklists.**

- They usually test fixed engineering criteria; this Skill first attacks whether the stage still has a right to exist, rather than endorsing an established plan's quality.
- They can inspect an execution result and then supply reasons for it; this Skill requires an independent auditor to form a counterfactual baseline from the original requirement and current facts first. A different executor solution can still pass if it is equally justified.
- They can re-review the whole task each round; this Skill freezes scope and revisits only conditions genuinely reopened by new evidence, preventing “more rigor” from becoming a reason for endless rework.

Use it for complex staged work whose next investment needs to be shown still worthwhile; formal objects or consequential external actions make the gate especially useful. Do not use it for simple reversible work, and do not treat it as an automated lock that decides for the executor.

### `plain-chinese`: explain the conclusion plainly without pretending uncertainty is settled

**Core problem.** An explanation, report, or proposal can be factually correct yet bury its conclusion in jargon, background, and lists. Readers then cannot tell what matters, what is confirmed, what is inferred, and what remains unknown.

This Skill states the core conclusion first, retains only the causal explanation that supports it, removes detail that does not change the judgment or next action, translates necessary jargon immediately, and labels confirmed facts, inferences, and uncertainty explicitly.

**How it differs from common summarization, translation, or copyediting tools.**

- They mainly compress content; this Skill makes the first sentence answer the reader's central question and keeps the causal chain needed to support it.
- They can make prose smoother while obscuring evidence strength; this Skill separates facts, inference, and unknowns.
- They can simplify by dropping action-relevant detail; this Skill removes only what does not affect the current judgment or next step.

Use it when the user asks for plain language, a simple explanation, conclusion first, less jargon, or explicit uncertainty. Do not use it where an exact legal, technical, or historical quotation must be preserved verbatim.

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
cp -R oh-my-skills/skills/plain-chinese "${CODEX_HOME:-$HOME/.codex}/skills/"
```

For a different Skill root, copy the corresponding `skills/<skill-name>` directory there.

## Invocation examples

```text
Use $requirement-definition to identify the irreducible requirement behind this proposal.

Use $first-principles-gate to establish a stage gate for this complex task.

Use $plain-chinese to explain this report plainly and state what remains uncertain.
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
    ├── plain-chinese/
    │   ├── SKILL.md
    │   └── agents/openai.yaml
    └── requirement-definition/
        ├── SKILL.md
        └── agents/openai.yaml
```

## Versioning and license

The project follows [Semantic Versioning](https://semver.org/); notable changes appear in [CHANGELOG.md](CHANGELOG.md).

[MIT](LICENSE)
