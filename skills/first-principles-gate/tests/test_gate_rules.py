from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


def require(text: str, marker: str, rule: str) -> None:
    if marker not in text:
        raise AssertionError(f"missing {rule}: {marker}")


def main() -> None:
    text = SKILL.read_text(encoding="utf-8")

    required_rules = {
        "evidence normalization": "设计、架构、计划、流程、测试和审计方法默认都是候选机制",
        "global minimum": "全局最小方案",
        "complexity burden": "谁主张新增长期复杂度，谁负责证明非加不可",
        "necessity proof": "删除它会让哪个当前用户结果通过哪条现实可达路径失败",
        "smaller alternative": "为什么一次性验证、人工恢复、局部重试或更小的可恢复方案不足",
        "complexity delta": "复杂度差额",
        "no local-minimum accumulation": "不得把逐项局部最小修正相加后直接视为整体最小",
        "single gate identity": "内部切面、Group、schema、字段、解析、状态机、超时、测试、重构和局部修复不构成新门禁",
        "correctness boundary": "普通正确性问题进入 TDD、代码评审或非阻塞 To Do",
        "revision direction": "证据不足时默认删除、降级或延后该机制",
        "auditor restraint": "审计者可以指出缺口，但不得把自己提出的复杂机制直接写成通过条件",
        "cumulative reset": "回到用户结果重新比较整体方案",
    }
    for rule, marker in required_rules.items():
        require(text, marker, rule)

    forbidden = [
        "每个阶段使用新鲜第一性原理门禁",
        "每个切面使用新鲜第一性原理门禁",
    ]
    for marker in forbidden:
        if marker in text:
            raise AssertionError(f"forbidden repeated-gate rule remains: {marker}")

    print("first-principles-gate complexity rules: PASS")


if __name__ == "__main__":
    main()
