# Oh My Skills

中文 | [English](README.en.md)

这是一个个人 Codex Skill 集合。每个 Skill 都是 `skills/` 下独立的同级目录；当前收录两个用于把复杂工作“想清楚、卡住边界”的 Skill。

## 先选哪一个

```text
还不确定真正要改变什么
  → requirement-definition

已经决定要做什么，但需要防止阶段越界、返工或无限审计
  → first-principles-gate
```

两者可以连续使用：先用 `requirement-definition` 确认需求核心，再用 `first-principles-gate` 为后续复杂阶段冻结通过条件。它们不替代设计、拆任务、实现或发布。

## 已收录技能

### `requirement-definition`：先确定“到底要解决什么”

它解决的核心问题是：讨论里混着痛点、方案、偏好、约束和猜测时，团队很容易把“目前想到的做法”当成真正需求，然后直接开始设计或拆任务。

它把问题画成需求树，以“谁需要改变 → 当前状态 → 必须发生的结果”为根。候选方案要经过删除检验：删掉它以后根问题仍在，它只是方案；删掉它以后需求变了，才是不可再删除的核心。每轮只问一个仍会改变根目标、价值排序、不可接受结果或边界的问题；前沿清空后才收敛。

它和普通需求澄清、PRD 生成或待办拆解 Skill 的不同是：

- 普通工具常把用户的第一种说法整理得更完整；它先检验这句话是否把方案、原因或价值判断混成了需求。
- 普通工具往往产出方案、优先级、任务列表或规格；它只产出根目标、需求核心、已确认边界和真正会改变判断的未定假设。
- 普通工具可能追求“问题问全”；它只保留当前有信息增益的一个问题，已关闭的分支不会反复打开。

适用：需求模糊、候选方案很多、目标冲突，或要在设计前确认“这件事为什么必须做”。

不适用：根目标和边界已经明确、现在只是实现一个低风险且可逆的小改动。

### `first-principles-gate`：让复杂阶段在证据边界内收口

它解决的核心问题是：复杂任务即使有计划，也可能在执行中不断扩大、反复换审计者、把“再严谨一点”当成持续返工理由，或者未经确认就跨过外部动作与副作用边界。

它为一个逻辑阶段设置门禁：新鲜的独立审计者先根据原始需求和当前事实盲审，冻结本阶段可观察的通过条件；执行中只有决定性的新证据才能局部重新打开条件；到下一个决策边界时，由同一审计者有限复查并输出 `PASS`、`REVISE` 或 `STOP`。它只能通过 `$first-principles-gate` 显式调用，不会自动介入普通任务。

它和普通代码审查、质量门禁或检查清单的不同是：

- 普通门禁通常检查固定的工程项目；它先检查当前阶段本身是否必要、是否越过授权／正式对象／外部动作的边界。
- 普通审计容易每轮重新全面审查；它先冻结范围，之后只复查被新证据真正打开的最小条件。
- 普通“更严谨”的建议可能一直阻塞推进；它只让有直接证据的必要性冲突、决定性事实缺失或严重难恢复风险触发 `REVISE`，其余记为非阻塞备注。

适用：复杂、分阶段、存在正式对象或关键外部动作的工作，且需要独立反证与明确收口。

不适用：简单、可逆、无需独立审计的小任务；也不能把它当成替执行者作决定的自动化锁。

## 安装

克隆仓库：

```bash
git clone https://github.com/HYBB-rash/oh-my-skills.git
```

复制需要的 Skill 到 Codex 默认目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R oh-my-skills/skills/requirement-definition "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R oh-my-skills/skills/first-principles-gate "${CODEX_HOME:-$HOME/.codex}/skills/"
```

若使用其他 Skill 根目录，只需把相应的 `skills/<skill-name>` 目录复制过去。

## 调用示例

```text
使用 $requirement-definition，找出这个方案背后不可再删除的需求核心。

使用 $first-principles-gate，为这个复杂任务建立阶段门禁。
```

## 仓库结构

```text
.
├── README.md                 # 中文默认首页
├── README.en.md              # 英文说明
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

## 版本管理与许可证

项目遵循[语义化版本](https://semver.org/lang/zh-CN/)，重要变化记录在 [CHANGELOG.md](CHANGELOG.md)。

[MIT](LICENSE)
