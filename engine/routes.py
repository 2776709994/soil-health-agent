"""三条路线比较、资源分配与决策规则。"""
from __future__ import annotations

from typing import Any

from .case_data import ROUTES, PLOTS
from .calc import resource_balance, budget_check, leaching
from .rules import diagnose_all


def route_compare(scenario: str = "base") -> dict[str, Any]:
    reduced = scenario == "reduced"
    routes = []
    for route in ROUTES:
        item = dict(route)
        item["cost_wan"] = route["cost_range_wan"]
        item["cost_note"] = "示意/学生模拟；需按查证单价替换"
        if reduced and route["id"] != "A":
            item["suitability"] = "条件性"
            item["scenario_tag"] = "供水 −25%：淋洗受限"
            item["note"] = item["note"] + " 供水上限降低后，S03–S05 只能分期/部分淋洗，优先 A + 覆盖/耐盐。"
        else:
            item["scenario_tag"] = ""
        routes.append(item)

    diagnostics = diagnose_all()["plots"]
    plot_plan = []
    for plot in diagnostics:
        if plot["drainage_key"] == "poor":
            route = "先排水 + 补测；C 条件性"
        elif plot["ece"] >= 4:
            route = "B + 定额淋洗（供水受限时分阶段）" if not reduced else "A + 覆盖/耐盐，淋洗受限"
        elif plot["ece"] >= 3:
            route = "A 为主，B 小试"
        else:
            route = "A 有机物料"
        plot_plan.append({
            "plot_id": plot["id"],
            "limits": plot["limits"],
            "route": route,
            "recommendation": plot["recommendation"],
            "missing": plot["missing"],
            "judgement": plot["judgement"],
        })

    return {
        "scenario": scenario,
        "routes": routes,
        "plot_plan": plot_plan,
        "decision": "S01–S02 以 A 为主；S03 走 B + 定额淋洗；S04–S05 先排水、补测 ESP/SAR/CEC，C 仅条件性。",
        "resource_balance": resource_balance(scenario),
        "budget": budget_check(scenario),
        "water": leaching("S03"),
        "citations": ["STD-01", "STD-02", "STD-03", "PAPER-02", "PAPER-03", "PAPER-04"],
        "assumptions": [
            "费用为示意区间，需按组员查证的单价替换；",
            "秸秆产炭率按干基 30%（文献范围 25–35%），需核对；",
            "淋洗按根层 0.6 m、稳态 LR 估算，不是完整水盐运移模型；",
            "ESP/SAR/CEC 缺失，钠化不可判定，C 不给精确石膏量。",
        ],
        "limitations": [
            "不能把 5 个地块结果外推为整个灌区；",
            "出苗率只描述现状，不是措施效果；",
            "标准阈值、单价、产率必须逐条核对后替换。",
        ],
    }
