# Requirement Definition

[简体中文](README.zh-CN.md) | English

A Codex skill for turning an uncertain discussion into the smallest confirmed requirement that must be satisfied.

It models the need as a requirement tree, separates candidate solutions from the irreducible core, and asks only one question at a time—the one whose answer can still change the goal, priority, unacceptable outcome, or boundary.

> This skill stops at requirement definition. It does not create a TODO plan, choose an implementation, or execute work.

## Core capabilities

- **Requirement tree:** express the root as “who needs to change → current state → required result,” with conditions, trade-offs, and assumptions as branches.
- **Deletion test:** distinguish a candidate solution from a core requirement by asking whether removing it changes the root need.
- **One decisive question:** keep only live conflicts and gaps whose answer can change the root goal, value order, unacceptable result, or boundary.
- **Evidence boundary:** verify checkable facts; leave values and boundaries to the user.
- **Explicit convergence:** when the frontier is empty, return the root goal, irreducible core, confirmed boundaries, and material unresolved assumptions.

## Install

Clone the repository:

```bash
git clone https://github.com/HYBB-rash/progressive-todo-tree.git
```

Copy the skill into the default Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R progressive-todo-tree/skills/requirement-definition "${CODEX_HOME:-$HOME/.codex}/skills/"
```

If your setup uses a different skill directory, copy `skills/requirement-definition` there instead. For example:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R progressive-todo-tree/skills/requirement-definition "$HOME/.agents/skills/"
```

## Use

Invoke it explicitly:

```text
Use $requirement-definition to identify the irreducible requirement behind this proposal.
```

Or describe the need naturally, for example:

```text
We have several proposed solutions and conflicting priorities. Help us define what must actually change before we design the system.
```

## Repository layout

```text
.
├── README.md
├── README.zh-CN.md
├── CHANGELOG.md
├── LICENSE
├── VERSION
└── skills/
    └── requirement-definition/
        ├── SKILL.md
        └── agents/openai.yaml
```

## Versioning

This project follows [Semantic Versioning](https://semver.org/). Public releases are tagged as `vMAJOR.MINOR.PATCH`; notable changes are recorded in [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE)
