# 需求定义

简体中文 | [English](README.md)

这是一个面向 Codex 的 Skill，用来把不确定的讨论收敛为必须满足、不可再删除的需求核心。

它用需求树表达问题，区分候选方案与真正需求，并且每轮只问一个问题：其答案仍可能改变根目标、价值排序、不可接受结果或边界的那一题。

> 这个 Skill 停在需求定义层，不生成 TODO 计划、不选择实现方案，也不执行工作。

## 核心能力

- **需求树：** 用“谁需要改变 → 当前状态 → 必须发生的结果”表达根节点；条件、取舍和假设是分支。
- **删除检验：** 删除后若根问题不变，它是候选方案；若需求改变，它才属于核心。
- **一个关键问题：** 只保留答案会改变根目标、价值排序、不可接受结果或边界的冲突与缺口。
- **证据边界：** 可查事实由 Agent 核验；价值和边界由用户决定。
- **明确收敛：** 前沿清空后，输出根目标、不可再删除的需求核心、已确认边界和会影响判断的未定假设。

## 安装

克隆仓库：

```bash
git clone https://github.com/HYBB-rash/progressive-todo-tree.git
```

复制到 Codex 默认 Skill 目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R progressive-todo-tree/skills/requirement-definition "${CODEX_HOME:-$HOME/.codex}/skills/"
```

如果你的环境使用其他 Skill 目录，将 `skills/requirement-definition` 复制过去即可。例如：

```bash
mkdir -p "$HOME/.agents/skills"
cp -R progressive-todo-tree/skills/requirement-definition "$HOME/.agents/skills/"
```

## 使用

可以直接点名：

```text
使用 $requirement-definition，找出这个方案背后不可再删除的需求核心。
```

也可以自然描述需求：

```text
我们有几个候选方案和互相冲突的优先级。请先定义真正需要改变什么，再进入系统设计。
```

## 仓库结构

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

## 版本管理

项目遵循[语义化版本](https://semver.org/lang/zh-CN/)。公开版本使用 `v主版本.次版本.修订号` 标签，重要变化记录在 [CHANGELOG.md](CHANGELOG.md) 中。

## 许可证

[MIT](LICENSE)
