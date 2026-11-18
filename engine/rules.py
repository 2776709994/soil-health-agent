"""可检查的专业规则。阈值均为教学/常用口径，正式引用前必须核对正式文本。"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from copy import deepcopy
from typing import Any

from .case_data import PLOTS, MISSING_FIELDS, ECW_DS_M, WATER_CAP_M3_PER_MU_YEAR


@dataclass
class RuleResult:
    rule_id: str
    name: str
    status: str
    severity: str
    conclusion: str
    evidence: list[str] = field(default_factory=list)
    inputs: dict[str, Any] = field(default_factory=dict)
    missing: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def salinity_class(ece: float | None) -> str:
    if ece is None:
        return "不可评价"
    if ece < 2:
        return "非盐化"
    if ece < 4:
        return "轻度"
    if ece < 8:
        return "中度"
    if ece < 16:
        return "重度"
    return "盐土"


def om_class(om: float | None) -> str:
    if om is None:
        return "不可评价"
    if om < 6:
        return "极低"
    if om < 10:
        return "很低"
    if om < 20:
        return "低"
    if om < 30:
        return "中"
    return "高"


def corn_yield_potential(ece: float | None) -> float | None:
    """仅按盐分胁迫估算，不是产量预测。阈值 1.7 dS/m、斜率 12%/dS/m。"""
    if ece is None:
        return None
    value = 1 - 0.12 * (ece - 1.7)
    return round(max(0.0, min(1.0, value)) * 100, 1)


def leaching_requirement(target_ece: float = 2.5, ecw: float = ECW_DS_M) -> dict[str, Any]:
    denominator = 5 * target_ece - ecw
    if denominator <= 0:
        return {"ok": False, "reason": "目标 ECe 过低，LR 无定义"}
    lr = ecw / denominator
    return {
        "ok": True,
        "ECw": ecw,
        "target_ECe": target_ece,
        "LR": round(lr, 4),
        "root_depth_m": 0.6,
    }


def evaluate_plot(
    plot: dict[str, Any],
    *,
    ec_method: str | None = "ECe_25C",
    esp: float | None = None,
    sar: float | None = None,
    cec: float | None = None,
    ions_provided: bool = False,
    drainage_destination: str | None = None,
    material_tested: bool = False,
) -> list[RuleResult]:
    ece = plot.get("ece")
    ph = plot.get("ph")
    bd = plot.get("bd")
    om = plot.get("om")
    drainage_key = plot.get("drainage_key")
    rules: list[RuleResult] = []

    # R01 EC 方法
    if ec_method != "ECe_25C":
        rules.append(RuleResult(
            "R01", "EC 测定方法", "not_evaluable", "high",
            "EC 方法不是 ECe（25℃饱和糊状土），不能按 ECe 阈值分级。",
            ["STD-02"], {"ec_method": ec_method}, ["ECe 25℃饱和糊状土"],
        ))
    else:
        rules.append(RuleResult(
            "R01", "EC 测定方法", "not_triggered", "info",
            "ECe 为 25℃饱和糊状土浸提液电导率，可按 ECe 阈值分级。",
            ["STD-02"], {"ec_method": ec_method},
        ))

    # R02 盐分分级
    if ec_method != "ECe_25C":
        rules.append(RuleResult(
            "R02", "盐分分级", "not_evaluable", "high",
            "EC 方法不满足 ECe，暂不能判定盐分等级。",
            ["STD-03"], {"ece": ece}, ["ECe 方法"],
        ))
    else:
        cls = salinity_class(ece)
        rules.append(RuleResult(
            "R02", "盐分分级", "triggered" if cls != "非盐化" else "not_triggered",
            "high" if cls in ("中度", "重度", "盐土") else "medium",
            f"ECe={ece} dS/m，盐分等级：{cls}。",
            ["STD-03"], {"ece": ece}, [],
        ))

    # R03 玉米耐盐
    yp = corn_yield_potential(ece)
    rules.append(RuleResult(
        "R03", "玉米耐盐", "triggered" if (yp is not None and yp < 100) else "not_triggered",
        "medium" if (yp is not None and yp < 80) else "info",
        f"仅按盐分胁迫估算，相对产量潜力约 {yp}%（不是产量预测）。" if yp is not None else "ECe 缺失，不能估算。",
        ["PAPER-01"], {"ece": ece, "threshold": 1.7, "slope": 0.12}, [] if yp is not None else ["ECe"],
    ))

    # R04 碱度
    if ph is not None and ph > 8.5:
        rules.append(RuleResult(
            "R04", "碱度", "triggered", "medium",
            f"pH={ph}（土:水=1:2.5）> 8.5，碱性强；pH 不能单独判定钠化。",
            ["STD-03"], {"ph": ph, "ph_method": "1:2.5"}, [],
        ))
    else:
        rules.append(RuleResult(
            "R04", "碱度", "not_triggered", "info",
            f"pH={ph}，未超过 8.5 的碱性提示阈值。", ["STD-03"], {"ph": ph}, [],
        ))

    # R05 钠化
    if esp is None or sar is None or cec is None:
        rules.append(RuleResult(
            "R05", "钠化判定", "not_evaluable", "high",
            "ESP/SAR/CEC 缺失，钠化程度暂不可判定；只能建议补测。",
            ["STD-03"], {"esp": esp, "sar": sar, "cec": cec}, ["ESP", "SAR", "CEC"],
        ))
    elif esp > 15 or sar > 13:
        rules.append(RuleResult(
            "R05", "钠化判定", "triggered", "high",
            f"ESP={esp}%、SAR={sar}，达到钠化判据；需结合 CEC 和排水条件。",
            ["STD-03"], {"esp": esp, "sar": sar, "cec": cec}, [],
        ))
    else:
        rules.append(RuleResult(
            "R05", "钠化判定", "not_triggered", "info",
            f"ESP={esp}%、SAR={sar}，未达到常用钠化判据；仍需按正式文本核对。",
            ["STD-03"], {"esp": esp, "sar": sar, "cec": cec}, [],
        ))

    # R06 有机质
    cls = om_class(om)
    rules.append(RuleResult(
        "R06", "有机质", "triggered" if cls in ("极低", "很低", "低") else "not_triggered",
        "medium" if cls in ("极低", "很低") else "info",
        f"有机质 {om} g/kg，等级：{cls}。", ["STD-03"], {"om_g_kg": om}, [],
    ))

    # R07 容重/结构
    if bd is not None and bd > 1.5:
        rules.append(RuleResult(
            "R07", "结构/容重", "triggered", "high",
            f"容重 {bd} g/cm³ > 1.5，明显压实，根系和入渗受限。",
            ["PAPER-05"], {"bd": bd}, [],
        ))
    elif bd is not None and bd > 1.4:
        rules.append(RuleResult(
            "R07", "结构/容重", "triggered", "medium",
            f"容重 {bd} g/cm³ > 1.4，开始限制根系。", ["PAPER-05"], {"bd": bd}, [],
        ))
    else:
        rules.append(RuleResult(
            "R07", "结构/容重", "not_triggered", "info",
            f"容重 {bd} g/cm³，未超过 1.4 的限制阈值。", ["PAPER-05"], {"bd": bd}, [],
        ))

    # R08 排水
    if drainage_key == "poor":
        rules.append(RuleResult(
            "R08", "排水条件", "triggered", "high",
            "排水较差；淋洗前必须明确排水去向、水质并完成改造，否则只给条件性建议。",
            ["STD-01"], {"drainage": plot.get("drainage"), "destination": drainage_destination},
            [] if drainage_destination else ["排水去向与水质"],
        ))
    else:
        rules.append(RuleResult(
            "R08", "排水条件", "not_triggered", "info",
            f"排水 {plot.get('drainage')}，可进一步评估淋洗；仍需确认去向。",
            ["STD-01"], {"drainage": plot.get("drainage")}, [] if drainage_destination else ["排水去向与水质"],
        ))

    # R09 淋洗配额
    lr = leaching_requirement()
    if lr.get("ok"):
        per_mu = lr["LR"] * lr["root_depth_m"] * 666.6667
        over = per_mu > WATER_CAP_M3_PER_MU_YEAR
        rules.append(RuleResult(
            "R09", "淋洗配额", "triggered" if over else "not_triggered",
            "high" if over else "medium",
            f"LR={lr['LR']}，按根层 0.6 m 约 {per_mu:.1f} m³/亩·年；"
            + ("超过 40 m³/(亩·年) 上限。" if over else "低于 40 m³/(亩·年) 上限，但仅为维持性估算。"),
            ["STD-01", "PAPER-06"],
            {"LR": lr["LR"], "root_depth_m": 0.6, "per_mu_m3": round(per_mu, 1)},
            [] if drainage_key != "poor" else ["排水改造/去向"],
        ))
    else:
        rules.append(RuleResult("R09", "淋洗配额", "not_evaluable", "high", lr.get("reason", ""), ["STD-01"], {}, ["ECw/目标 ECe"]))

    # R10 灌溉水水质
    rules.append(RuleResult(
        "R10", "灌溉水水质", "not_evaluable" if not ions_provided else "not_triggered",
        "medium" if not ions_provided else "info",
        "ECw=0.8 dS/m；SAR、Cl⁻ 等主要离子缺失，暂不能评价钠害/氯害。" if not ions_provided
        else "ECw=0.8 dS/m，主要离子已提供，可进一步评价。",
        ["STD-01"], {"ecw": ECW_DS_M}, [] if ions_provided else ["主要离子"],
    ))

    # R11 材料品质
    rules.append(RuleResult(
        "R11", "材料品质", "not_evaluable" if not material_tested else "not_triggered",
        "medium" if not material_tested else "info",
        "粪肥含水率、盐分、重金属、腐熟度未提供，材料品质待检。" if not material_tested
        else "材料品质已提供，可按检测结果调整用量。",
        ["STD-03"], {"material_tested": material_tested}, [] if material_tested else ["粪肥品质"],
    ))

    # R12 转化产率
    rules.append(RuleResult(
        "R12", "原料→成品", "not_triggered", "info",
        "秸秆制炭/堆肥必须按干基产率折算成品，不能把原料质量当成品量；产率需文献支撑。",
        ["PAPER-04"], {"straw_biochar_yield": "25–35%", "compost_yield": "40–60%"}, [],
    ))

    # R13 资源、R14 预算为全局规则，在 routes 中检查

    return rules


def diagnose_plot(
    plot: dict[str, Any],
    *,
    ec_method: str | None = "ECe_25C",
    esp: float | None = None,
    sar: float | None = None,
    cec: float | None = None,
    ions_provided: bool = False,
    drainage_destination: str | None = None,
    material_tested: bool = False,
) -> dict[str, Any]:
    rules = evaluate_plot(
        plot, ec_method=ec_method, esp=esp, sar=sar, cec=cec,
        ions_provided=ions_provided, drainage_destination=drainage_destination,
        material_tested=material_tested,
    )
    rule_dicts = [r.to_dict() for r in rules]
    triggered = [r for r in rules if r.status == "triggered"]
    not_evaluable = [r for r in rules if r.status == "not_evaluable"]
    ece = plot.get("ece")
    cls = salinity_class(ece)
    yp = corn_yield_potential(ece)
    drainage_key = plot.get("drainage_key")

    if drainage_key == "poor":
        recommendation = "先排水"
    elif ece is not None and ece >= 4:
        recommendation = "B+淋洗"
    elif ece is not None and ece >= 3:
        recommendation = "A/B"
    else:
        recommendation = "A"

    missing = sorted({m for r in rules for m in r.missing})
    return {
        **plot,
        "salt_class": cls,
        "yield_potential": yp,
        "recommendation": recommendation,
        "rule_results": rule_dicts,
        "triggered_rule_ids": [r.rule_id for r in triggered],
        "not_evaluable_rule_ids": [r.rule_id for r in not_evaluable],
        "missing": missing or ["ESP", "SAR", "CEC"],
        "status": "limited" if drainage_key == "poor" else ("watch" if ece and ece >= 4 else plot.get("status", "normal")),
        "judgement": "条件性" if drainage_key == "poor" or missing else "可判定",
    }


def qc(plots: list[dict[str, Any]] | None = None, ec_method: str = "ECe_25C") -> dict[str, Any]:
    data = plots or PLOTS
    errors: list[dict[str, Any]] = []
    for p in data:
        pid = p.get("id", "?")
        ranges = {
            "ph": (3.0, 11.0), "ece": (0.0, 60.0), "om": (0.0, 100.0),
            "bd": (0.8, 2.0), "emergence": (0.0, 100.0),
        }
        for key, (low, high) in ranges.items():
            value = p.get(key)
            if value is None:
                errors.append({"plot_id": pid, "field": key, "issue": "missing"})
            elif not isinstance(value, (int, float)) or value < low or value > high:
                errors.append({"plot_id": pid, "field": key, "issue": "out_of_range", "value": value, "range": [low, high]})
    if ec_method != "ECe_25C":
        errors.append({"plot_id": "all", "field": "ec_method", "issue": "method_not_ECe", "value": ec_method})
    checks = [
        {"item": "单位与量纲", "result": "通过" if not errors else "需检查", "detail": "pH 1:2.5；ECe dS/m；有机质 g/kg；容重 g/cm³；出苗率 %"},
        {"item": "缺失值", "result": "通过" if not any(e["issue"] == "missing" for e in errors) else "有缺失", "detail": "ESP、SAR、CEC、排水去向、主要离子"},
        {"item": "负值与异常", "result": "通过" if not errors else "需检查", "detail": "5 个地块范围检查"},
        {"item": "EC 测定方法", "result": "通过" if ec_method == "ECe_25C" else "不可评价", "detail": ec_method},
        {"item": "钠化判定", "result": "不可判定", "detail": "缺 ESP/SAR/CEC，不能仅凭 pH/ECe 判定"},
        {"item": "排水条件", "result": "部分缺失", "detail": "排水分级已有，去向与水质未提供"},
        {"item": "材料品质", "result": "未提供", "detail": "粪肥含水率、盐分、重金属、腐熟度"},
        {"item": "出苗率", "result": "仅现状", "detail": "只能描述现状，不能作为措施效果"},
    ]
    return {"checks": checks, "errors": errors, "passed": not errors, "missing_fields": MISSING_FIELDS, "plot_count": len(data)}


def diagnose_all(overrides: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    overrides = overrides or {}
    result = []
    for base in PLOTS:
        plot = deepcopy(base)
        extra = overrides.get(plot["id"], {})
        plot.update({k: v for k, v in extra.items() if k in {"drainage", "drainage_key", "ph", "ece", "om", "bd", "emergence"}})
        diag = diagnose_plot(
            plot,
            ec_method=extra.get("ec_method", "ECe_25C"),
            esp=extra.get("esp"),
            sar=extra.get("sar"),
            cec=extra.get("cec"),
            ions_provided=extra.get("ions_provided", False),
            drainage_destination=extra.get("drainage_destination"),
            material_tested=extra.get("material_tested", False),
        )
        result.append(diag)
    return {
        "plots": result,
        "missing_fields": MISSING_FIELDS,
        "sodicity_note": "5 个地块均缺 ESP/SAR/CEC，钠化程度暂不可判定；pH 只说明碱性强，不能判钠化。",
        "data_note": "教师给定教学数据；标准/单价/产率需按正式文本和本地询价核对。",
    }
