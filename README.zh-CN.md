# 渐进式 TODO 树

简体中文 | [English](README.md)

这是一个面向 Codex 的 Skill，用来让长期、复杂、充满不确定性的规划保持精简、透明、可复审，并能跨会话继续。

它会维护持久化 TODO 树，从第一性原理重建重要问题，在明显投入前压缩预算，识别路线失稳，并把已关闭分支归档到活跃状态之外。

> 这个 Skill 只负责规划、判断和维护状态，不执行 TODO 树里的实际任务。

## 核心能力

- **权威状态：** 从用户指定的 `TODO.md`、当前项目的 `TODO.md`，或用户提供的 Notion 目标继续工作。
- **第一性原理：** 在接受某个方案为必要条件前，先区分可观察结果、当前事实、硬约束和未验证假设。
- **预算压缩：** 比较相对的 `1000 / 100 / 10` 投入档位，选择能保住关键结果的最低投入。
- **干净的双层树：** 顶部只保留给人看的复选框树，下面保存精简的 Agent 接管信息。
- **路线复审：** 公开路线假设与反证；当局部工作回答不了根问题时，暂停继续扩张。
- **暂停与恢复：** 保留路线为何停止，但不给旧路线默认的“最后再试一次”。
- **分支归档：** 把关闭的顶层分支移入按日期命名的归档文件，活跃 TODO 只保留简短索引和恢复条件。

## 核心工作顺序

1. 不借用当前方案的名字，先说清最终要发生的可观察变化。
2. 把事实和硬约束，与假设和实现偏好分开。
3. 找到能够保住核心结果的最小行动。
4. 活跃树只具体展开当前获批的预算档位。
5. 记录什么证据允许追加投入，什么证据会触发路线复审。
6. 顶层分支完成、放弃、暂停或被替代后，将其压缩归档。

## 安装

克隆仓库：

```bash
git clone https://github.com/HYBB-rash/progressive-todo-tree.git
```

复制到 Codex 默认 Skill 目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R progressive-todo-tree/skills/progressive-todo-tree "${CODEX_HOME:-$HOME/.codex}/skills/"
```

如果你的环境使用其他 Skill 目录，将 `skills/progressive-todo-tree` 复制过去即可。例如：

```bash
mkdir -p "$HOME/.agents/skills"
cp -R progressive-todo-tree/skills/progressive-todo-tree "$HOME/.agents/skills/"
```

## 使用

可以直接点名：

```text
使用 $progressive-todo-tree，把这个不确定的项目整理成一棵最小、可持久化的 TODO 树。
```

也可以自然描述需求：

```text
帮我找出不能牺牲的核心结果，把第一笔预算从 1000 压到 100 或 10，并让这条路线以后可以继续复审。
```

如果要把状态存入 Notion，请提供你自己的页面或数据库。公开仓库不包含任何个人工作区标识。

## 仓库结构

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

## 版本管理

项目遵循[语义化版本](https://semver.org/lang/zh-CN/)。公开版本使用 `v主版本.次版本.修订号` 标签，重要变化记录在 [CHANGELOG.md](CHANGELOG.md) 中。

最初的 `0.x` 系列表示：Skill 已经可用并通过场景测试，但长期真实规划中的表现仍需继续观察。

## 许可证

[MIT](LICENSE)
