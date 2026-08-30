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

它解决的核心问题是：需求已经说得差不多时，澄清过程仍会不断凭空增加边缘问题，或把已经回答的分支换一种说法重新打开，最后“继续澄清”变成无法结束的想象力竞赛。

它把问题画成需求树，以“谁需要改变 → 当前状态 → 必须发生的结果”为根。候选方案要经过删除检验：删掉它以后根问题仍在，它只是方案；删掉它以后需求变了，才是不可再删除的核心。问题只能来自当前材料已经出现的冲突和缺口；每轮只问一个仍会改变判断的问题，已回答分支保持关闭，前沿清空后立即收敛。

它和普通需求澄清、PRD 生成或待办拆解 Skill 的不同是：

- 普通工具常把用户的第一种说法整理得更完整；它先检验这句话是否把方案、原因或价值判断混成了需求。
- 普通工具往往产出方案、优先级、任务列表或规格；它只产出根目标、需求核心、已确认边界和真正会改变判断的未定假设。
- 普通工具可能追求“问题问全”，于是不断补充假想边缘情况；它不从材料外发明分支，只保留当前有信息增益的一个问题，已关闭的分支不会反复打开。

适用：需求仍有会改变结果的真实冲突或缺口，但讨论已经开始反复、扩张，或需要在进入设计前确认“这件事为什么必须做”。

不适用：根目标和边界已经明确、现在只是实现一个低风险且可逆的小改动。

### `first-principles-gate`：让复杂阶段在证据边界内收口

它解决的核心问题是：复杂任务已经有计划、已经投入，甚至已经得到过一次通过后，执行者仍可能因为沉没成本、惯性或自我合理化，继续完成那些当下已经无法从原始需求和当前事实推出的工作。

它为一个逻辑阶段设置门禁：执行者先证明当前规划、阶段和产物为何仍由原始需求与事实推出；新鲜的独立审计者在接触执行结果前先盲审并主动寻找有证据的反例，冻结本阶段可观察的通过条件。执行中只有决定性的新证据才能局部重新打开条件；到下一个决策边界时，由同一审计者有限复查并输出 `PASS`、`REVISE` 或 `STOP`。一次历史 `PASS` 不是永久凭证。它只能通过 `$first-principles-gate` 显式调用，不会自动介入普通任务。

它和普通代码审查、质量门禁或检查清单的不同是：

- 普通门禁通常检查固定的工程项目是否达标；它首先攻击的是“这段工作现在还有没有存在资格”，而不是替既有计划做质量背书。
- 普通审计可能先看执行结果，再替执行者补理由；它要求独立审计者先从原始需求和当前事实出发形成反事实基准，执行者不同的方案只要同样成立也可以通过。
- 普通审计容易每轮重新全面审查；它先冻结范围，之后只复查被新证据真正打开的最小条件。这样避免把“可以更严谨”误当成继续返工的理由。

适用：复杂、分阶段的工作，且下一段需要重新证明仍值得投入；正式对象或关键外部动作会让这个门禁尤其必要。

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
