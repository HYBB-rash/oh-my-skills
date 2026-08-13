# Progressive TODO Tree

[简体中文](README.zh-CN.md) | English

A Codex skill for keeping long, uncertain planning work small, explicit, reviewable, and easy to resume across sessions.

It maintains a persistent TODO tree, rebuilds important problems from first principles, compresses budget before major investment, detects route drift, and archives closed branches without polluting the active state.

> This skill plans, reasons, and maintains state. It does not execute the substantive tasks inside the TODO tree.

## Core capabilities

- **Authoritative state:** continue from a user-provided `TODO.md`, the current project's `TODO.md`, or a user-provided Notion target.
- **First-principles reconstruction:** separate observable outcomes, current facts, hard constraints, and unverified assumptions before accepting a solution as necessary.
- **Budget compression:** compare relative `1000 / 100 / 10` investment levels and choose the cheapest level that preserves the decision-critical result.
- **Clean dual-layer tree:** keep a human-facing checkbox tree at the top and compact handoff context below it.
- **Route review:** expose route assumptions and disconfirming evidence; pause expansion when local work no longer answers the root question.
- **Pause and recovery:** preserve why a route stopped without granting it an automatic “one last experiment.”
- **Branch archives:** move closed top-level branches into dated archive files while keeping a short recovery index in the active TODO.

## Core loop

1. State the desired observable result without naming the current solution.
2. Separate facts and hard constraints from assumptions and implementation preferences.
3. Find the smallest action that can preserve the core result.
4. Make only the currently approved budget level concrete in the active tree.
5. Record what evidence would justify more investment or force route review.
6. Archive a top-level branch when it is completed, abandoned, paused, or replaced.

## Install

Clone the repository:

```bash
git clone https://github.com/HYBB-rash/progressive-todo-tree.git
```

Copy the skill into the default Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R progressive-todo-tree/skills/progressive-todo-tree "${CODEX_HOME:-$HOME/.codex}/skills/"
```

If your setup uses a different skill directory, copy `skills/progressive-todo-tree` there instead. For example:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R progressive-todo-tree/skills/progressive-todo-tree "$HOME/.agents/skills/"
```

## Use

Invoke it explicitly:

```text
Use $progressive-todo-tree to turn this uncertain project into a minimal, persistent TODO tree.
```

Or describe the need naturally, for example:

```text
Help me identify the non-negotiable result, compress the first budget from 1000 to 100 or 10, and keep the route reviewable across sessions.
```

For Notion persistence, provide your own page or database target. This public repository contains no personal workspace identifiers.

## Repository layout

```text
.
├── README.md
├── README.zh-CN.md
├── CHANGELOG.md
├── LICENSE
├── VERSION
└── skills/
    └── progressive-todo-tree/
        ├── SKILL.md
        └── agents/openai.yaml
```

## Versioning

This project follows [Semantic Versioning](https://semver.org/). Public releases are tagged as `vMAJOR.MINOR.PATCH`; notable changes are recorded in [CHANGELOG.md](CHANGELOG.md).

The initial `0.x` series indicates that the skill is usable and scenario-tested, while its long-term behavior is still being learned through real planning work.

## License

[MIT](LICENSE)
