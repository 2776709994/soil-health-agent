"""确定性报告生成：two-year plan / summary。"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .case_data import PLOTS, MISSING_FIELDS, BUDGET_CNY, WATER_CAP_M3_PER_MU_YEAR
from .calc import soil_mass, material_need, leaching
from .rules import diagnose_all
from .routes import route_compare

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "agent-workspace" / "outputs"


def _diagnosis_table() -> str:
    rows = ["| 地块 | pH (1:2.5) | ECe (dS/m) | 有机质 (g/kg) | 容重 (g/cm³) | 排水 | 出苗率 (%) | 主要限制 | 建议 |",
            "|---|---:|---:|---:|---:|---|---:|---|---|"]
    for p in diagnose_all()["plots"]:
        rows.append(
            f"| {p['id']} | {p['ph']:.1f} | {p['ece']:.1f} | {p['om']} | {p['bd']:.2f} | "
            f"{p['drainage']} | {p['emergence']} | {'、'.join(p['limits'])} | {p['recommendation']} |"
        )
    return "\n".join(rows)


def _material_table() -> str:
    rows = ["| 地块 | M（t，干基） | 折合 t/亩 | 示例材料 | 成品量 | 原料量（示例） |",
            "|---|---:|---:|---|---:|---:|"]
    for plot in PLOTS:
        mass = soil_mass(plot["id"])
        if plot["id"] in ("S01", "S02"):
            need = material_need(plot["id"], rate_t_per_ha=7.5, raw_to_product_yield=0.5)
            material = "腐熟粪肥（成品）7.5 t/ha"
        elif plot["id"] == "S03":
            need = material_need(plot["id"], rate_t_per_ha=3.0, raw_to_product_yield=0.30)
            material = "生物炭 3 t/ha（秸秆制炭）"
        else:
            need = material_need(plot["id"], rate_t_per_ha=0, raw_to_product_yield=0.30)
            material = "暂不施炭/钙基；先排水、补测"
        raw = "—" if need["raw_material_t"] is None else f"{need['raw_material_t']} t"
        rows.append(
            f"| {plot['id']} | {mass['M_t']:,} | {mass['per_mu_t']} | {material} | "
            f"{need['product_t']} t | {raw} |"
        )
    return "\n".join(rows)


def _monitoring_table() -> str:
    rows = ["| 指标 | 频率 | 点位 | 目的 |", "|---|---|---|---|"]
    rows += [
        "| ECe、pH | 每年 2 次 | 5 个地块 | 盐分/碱度变化 |",
        "| ESP、SAR、CEC | 基线 + 第 2 年 | 5 个地块 | 钠化判定 |",
        "| 有机质、容重 | 每年 1 次 | 5 个地块 | 结构与肥力 |",
        "| 出苗率、产量 | 每季 | 5 个地块 | 现状与效果（描述性） |",
        "| 排水、水位 | 每季 | S04/S05 | 排水与盐分去向 |",
    ]
    return "\n".join(rows)


def build_two_year_plan() -> str:
    compare = route_compare("base")
    water = leaching("S03")
    return f"""# 盐碱化耕地两年实施与监测计划（200 亩 / 5 地块）

> **数据分层**：地块 pH、ECe、有机质、容重、出苗率、排水、面积、预算、淋洗上限、ECw、秸秆/粪肥量 = **教师给定**；标准号、阈值、论文 = **待核对/待替换**；单价、产率、费用区间 = **学生模拟**。
>
> **声明**：教学模拟数据，不替代实测、法定评估或田间试验。

## 1. 结论先行

- 不是三选一：S01/S02 走 A（有机物料），S03 走 B（炭化 + 定额淋洗），S04/S05 两年内以**排水改造 + 覆盖压盐 + 分期淋洗 + 有机改良**为主，C（钙基）只做**条件性预留**。
- 5 个地块均缺 ESP/SAR/CEC，**钠化程度不可判定**；不得给精确石膏用量，也不得判“非钠化”。
- 淋洗 40 m³/(亩·年) 只够**维持/压盐**，不足以两年内把 S05 洗到 2.5 dS/m；S04/S05 必须先解决排水去向与水质。
- 预算 60 万元；A/B/C 费用区间分别约 24–36、36–50、50–70 万元/两年（示意），C 可能超预算。

## 2. 分地块诊断

{_diagnosis_table()}

**钠化说明**：ESP/SAR/CEC、主要离子、排水去向及水质未提供；pH 9.3–9.5 只说明碱性强，不能据此判钠化。

## 3. 三条路线比较

| 路线 | 措施 | 适用地块 | 先决条件 | 两年费用（示意） | 适用性 | 主要限制 |
|---|---|---|---|---|---|---|
| A 有机物料主导 | 腐熟粪肥 + 秸秆堆肥还田 | S01–S02 | 粪肥腐熟；盐分/重金属合格 | 24–36 万元 | 高 | 粪肥盐分可能抬高 ECe |
| B 秸秆炭化 + 定额淋洗 | 生物炭 + 粪肥 + 限额淋洗 | S02–S04 | 排水可用；生物炭 pH/灰分合格 | 36–50 万元 | 中 | 生物炭偏碱；淋洗受 40 m³/亩·年限制 |
| C 钙基 + 排水 | 石膏/钙基 + 排水改造 + 淋洗 | S04–S05（条件性） | ESP/SAR/CEC 可得；排水去向明确 | 50–70 万元 | 条件性 | 参数缺失，不能给精确石膏量；可能超预算 |

**推荐组合**：S01–S02 A；S03 B + 定额淋洗；S04–S05 先排水、补测，C 仅条件性。

## 4. 材料、水量与费用口径

**干土质量**：M = A × d × ρ；1 亩 = 666.6667 m²；d = 0.2 m。

{_material_table()}

**淋洗**：LR = ECw / (5×ECe,t − ECw)；按 ECe,t=2.5、ECw=0.8、根层 0.6 m，LR≈{water['LR']}，约 {water['per_mu_m3_year']} m³/亩·年，低于 {WATER_CAP_M3_PER_MU_YEAR} m³/(亩·年) 上限；这是维持性估算，不是完整水盐运移模型。

**资源**：秸秆 80 t（干基）按 30% 产炭率约 24 t 生物炭；按 3 t/ha 只够约 3 个地块，不能 5 块均摊。粪肥 100 t（干基）按 7.5 t/ha 约覆盖 5 块；S04/S05 若粪肥盐分高应减量。**原料 ≠ 成品，干基/湿基分开。**

**费用**：材料 + 运输 + 施用/施工 + 排水改造 + 监测 + 管理；单价需组员查证，当前区间为示意/学生模拟。

## 5. 两年实施计划

| 时间 | 任务 |
|---|---|
| 第 1 年 Q1–Q2 | 补测 ESP/SAR/CEC、主要离子；排水去向与水质调查；S04/S05 排水改造；S01/S02 粪肥 + 堆肥 |
| 第 1 年 Q3–Q4 | S03 生物炭 + 定额淋洗；监测 ECe/pH/ESP；记录淋洗水量；调整 S04/S05 措施 |
| 第 2 年 Q1–Q2 | 补施有机物料；S04/S05 分阶段；复测 ESP/SAR/CEC；评估钠化变化 |
| 第 2 年 Q3–Q4 | 监测出苗率/产量；汇总费用与水量；形成两年报告；提出第三年建议 |

## 6. 监测计划

{_monitoring_table()}

> 出苗率只用于描述现状，不作为措施效果；效果验证需对照与重复监测。

## 7. 数据缺口与限制

- ESP、SAR、CEC、主要离子缺失：钠化不可判定；C 路线不能给精确石膏用量。
- 排水去向及水质缺失：S04/S05 淋洗只能条件性建议。
- 粪肥品质未检测：材料用量需按含水率、盐分、重金属、腐熟度调整。
- 费用、产率、单价为示意/学生模拟；标准阈值需逐项核对。
- 本计划不能外推为整个灌区结论；不能替代法定检测或田间试验。

## 8. 依据（占位，待核对）

- STD-01 农田灌溉水质标准（版本待核对）
- STD-02 土壤检测方法：pH、ECe、有机质、CEC（待核对）
- STD-03 盐渍化分级与改良技术资料（版本待核对）
- PAPER-02 石膏改良钠化土壤（待替换）
- PAPER-03 生物炭改良盐碱土（待替换）
- PAPER-04 秸秆炭化产率与还田（待替换）
"""


def write_report(kind: str = "two_year_plan") -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if kind not in {"two_year_plan", "summary"}:
        raise ValueError("kind 仅支持 two_year_plan / summary")
    if kind == "two_year_plan":
        content = build_two_year_plan()
        filename = "two-year-plan.md"
    else:
        compare = route_compare("base")
        content = "# 摘要\n\n" + compare["decision"] + "\n\n" + "\n".join(
            f"- {p['plot_id']}：{p['route']}" for p in compare["plot_plan"]
        )
        filename = "soil-summary.md"
    path = OUTPUT_DIR / filename
    path.write_text(content, encoding="utf-8")
    return {
        "path": str(path),
        "relative_path": f"outputs/{filename}",
        "bytes": len(content.encode("utf-8")),
        "sections": ["结论", "诊断", "路线", "材料/水量/费用", "两年计划", "监测", "缺口", "依据"],
        "note": "确定性模板生成；标准/单价/产率仍需组员核对。",
    }
