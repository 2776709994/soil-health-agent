"""Soil Health MCP tools for 题目二.

Run:
    python -m engine.mcp_server
Endpoint:
    http://127.0.0.1:8100/mcp
"""
from __future__ import annotations

import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from .calc import (
    soil_mass,
    material_need,
    leaching,
    resource_balance,
    budget_check,
    gypsum_requirement,
)
from .rules import qc, diagnose_all
from .routes import route_compare
from .report import write_report

mcp = FastMCP(
    "soil-health-engine",
    instructions=(
        "盐碱化耕地土壤健康诊断与精准改良引擎。所有数字以本工具返回为准；"
        "ESP/SAR/CEC 缺失时不得判钠化、不得给精确石膏用量；"
        "费用/产率/单价为示意或学生模拟，需标注。"
    ),
    host=os.environ.get("SOIL_MCP_HOST", "127.0.0.1"),
    port=int(os.environ.get("SOIL_MCP_PORT", "8100")),
)


@mcp.tool()
def soil_qc(
    plots: list[dict[str, Any]] | None = None,
    ec_method: str = "ECe_25C",
) -> dict[str, Any]:
    """检查单位、缺失值、负值、EC/pH 方法口径，返回质控清单与缺失字段。

    plots 可传自定义地块数据；ec_method 必须是 ECe_25C（25℃饱和糊状土）才可按 ECe 分级。
    """
    return qc(plots, ec_method)


@mcp.tool()
def soil_diagnose(overrides: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    """诊断 5 个地块：盐分、钠化、有机质、容重、排水、出苗率、主要限制与建议。

    overrides 可用于测试：{plot_id: {esp, sar, cec, ec_method, drainage, drainage_key, ...}}。
    ESP/SAR/CEC 缺失时，钠化会返回 not_evaluable；不得据此判钠化。
    """
    return diagnose_all(overrides)


@mcp.tool()
def soil_calc_material(
    plot_id: str,
    rate_t_per_ha: float | None = None,
    rate_fraction: float | None = None,
    raw_to_product_yield: float = 0.3,
) -> dict[str, Any]:
    """计算地块干土质量 M 与材料需求 Q（含原料→成品、干基口径）。

    参数二选一：rate_t_per_ha（t/ha，成品）或 rate_fraction（以干土质量为基准）。
    """
    mass = soil_mass(plot_id)
    if rate_t_per_ha is None and rate_fraction is None:
        return {
            "plot_id": plot_id,
            "mass": mass,
            "status": "need_rate",
            "message": "请给出 rate_t_per_ha 或 rate_fraction；不得把原料质量当成品量。",
        }
    need = material_need(
        plot_id,
        rate_t_per_ha=rate_t_per_ha,
        rate_fraction=rate_fraction,
        raw_to_product_yield=raw_to_product_yield,
    )
    return {"mass": mass, "material": need, "status": "ok"}


@mcp.tool()
def soil_calc_water(
    plot_id: str = "S03",
    target_ece: float = 2.5,
    root_depth_m: float = 0.6,
) -> dict[str, Any]:
    """计算淋洗需水 LR、m³/亩·年、与 40 m³/(亩·年) 上限比较。

    注意：这是稳态维持性估算，不是完整水盐运移模型；初始盐分高时两年内不能降到目标值。
    """
    result = leaching(plot_id, target_ece=target_ece, root_depth_m=root_depth_m)
    result["status"] = "ok" if result.get("within_cap") is not None else "invalid"
    return result


@mcp.tool()
def soil_compare_routes(scenario: str = "base") -> dict[str, Any]:
    """比较 A 有机物料、B 秸秆炭化+淋洗、C 钙基+排水；返回资源、水量、预算、分地块建议。

    scenario: base（40 m³/亩·年）或 reduced（30 m³/亩·年）。
    """
    if scenario not in ("base", "reduced"):
        return {"status": "invalid", "message": "scenario 仅支持 base / reduced"}
    result = route_compare(scenario)
    result["status"] = "ok"
    result["resource_balance_alt"] = resource_balance(scenario)
    result["budget_alt"] = budget_check(scenario)
    return result


@mcp.tool()
def soil_write_report(kind: str = "two_year_plan") -> dict[str, Any]:
    """生成确定性报告文件到 agent-workspace/outputs/。

    kind: two_year_plan（完整两年计划）或 summary（简短摘要）。
    返回相对路径、字节数、章节和声明。
    """
    return write_report(kind)


@mcp.tool()
def soil_gypsum_check(
    plot_id: str | None = None,
    cec_cmol_kg: float | None = None,
    esp_percent: float | None = None,
    target_esp_percent: float = 5.0,
    rho_b: float = 1.54,
    depth_cm: float = 20.0,
) -> dict[str, Any]:
    """条件性石膏估算。ESP 或 CEC 缺失时必须返回 refused，不得给精确用量。

    公式 GR=0.086×CEC×ΔESP×ρb×d（kg/ha），系数和适用边界需正式文本核对。
    plot_id 仅用于回显；当前 5 个地块均缺 ESP/SAR/CEC。
    """
    result = gypsum_requirement(
        cec_cmol_kg=cec_cmol_kg,
        esp_percent=esp_percent,
        target_esp_percent=target_esp_percent,
        rho_b=rho_b,
        depth_cm=depth_cm,
    )
    if plot_id:
        result["plot_id"] = plot_id
    return result


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
