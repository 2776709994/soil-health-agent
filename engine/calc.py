"""定量计算：M=A·d·ρ、Q=M·r、LR、原料→成品、资源平衡。"""
from __future__ import annotations

from typing import Any

from .case_data import (
    PLOTS, MU_M2, DEPTH_M, ROOT_DEPTH_M, AREA_PER_PLOT_MU,
    WATER_CAP_M3_PER_MU_YEAR, ECW_DS_M, STRAW_T, MANURE_T,
    STRAW_BIOCHAR_YIELD, BUDGET_CNY,
)


def get_plot(plot_id: str) -> dict[str, Any]:
    for plot in PLOTS:
        if plot["id"] == plot_id:
            return plot
    raise ValueError(f"unknown plot: {plot_id}")


def soil_mass(plot_id: str, area_mu: float | None = None, depth_m: float = DEPTH_M) -> dict[str, Any]:
    plot = get_plot(plot_id)
    area_mu = plot["area_mu"] if area_mu is None else area_mu
    area_m2 = area_mu * MU_M2
    mass_t = area_m2 * depth_m * plot["bd"]
    per_mu_t = MU_M2 * depth_m * plot["bd"]
    return {
        "plot_id": plot_id,
        "area_mu": area_mu,
        "area_m2": round(area_m2, 1),
        "depth_m": depth_m,
        "bulk_density_t_m3": plot["bd"],
        "M_t": round(mass_t, 1),
        "per_mu_t": round(per_mu_t, 1),
        "formula": "M = A × d × ρ",
        "basis": "干基；0–20 cm 改良层",
    }


def material_need(
    plot_id: str,
    *,
    rate_fraction: float | None = None,
    rate_t_per_ha: float | None = None,
    raw_to_product_yield: float = STRAW_BIOCHAR_YIELD,
) -> dict[str, Any]:
    mass = soil_mass(plot_id)
    area_ha = mass["area_m2"] / 10_000
    if rate_t_per_ha is not None:
        product_t = rate_t_per_ha * area_ha
        source = f"{rate_t_per_ha} t/ha × {area_ha:.3f} ha"
    elif rate_fraction is not None:
        product_t = mass["M_t"] * rate_fraction
        source = f"M × {rate_fraction}"
    else:
        raise ValueError("rate_fraction 或 rate_t_per_ha 必须给出一个")
    raw_t = product_t / raw_to_product_yield if raw_to_product_yield else None
    return {
        "plot_id": plot_id,
        "product_t": round(product_t, 2),
        "rate_source": source,
        "raw_material_t": round(raw_t, 2) if raw_t is not None else None,
        "yield_ratio": raw_to_product_yield,
        "formula": "Q = M × r 或 Q = rate × area；原料 = 成品 / 产率",
        "basis": "干基；原料/成品分开",
        "note": "产率需文献支撑；不得把原料质量当成品量。",
    }


def leaching(plot_id: str, target_ece: float = 2.5, root_depth_m: float = ROOT_DEPTH_M) -> dict[str, Any]:
    plot = get_plot(plot_id)
    if 5 * target_ece - ECW_DS_M <= 0:
        return {"plot_id": plot_id, "status": "invalid", "reason": "目标 ECe 过低"}
    lr = ECW_DS_M / (5 * target_ece - ECW_DS_M)
    per_mu_m3 = lr * root_depth_m * MU_M2
    total_m3 = per_mu_m3 * plot["area_mu"]
    cap_total = WATER_CAP_M3_PER_MU_YEAR * plot["area_mu"]
    return {
        "plot_id": plot_id,
        "ECw_dS_m": ECW_DS_M,
        "target_ECe_dS_m": target_ece,
        "root_depth_m": root_depth_m,
        "LR": round(lr, 4),
        "per_mu_m3_year": round(per_mu_m3, 1),
        "total_m3_year": round(total_m3, 0),
        "cap_m3_per_mu_year": WATER_CAP_M3_PER_MU_YEAR,
        "within_cap": per_mu_m3 <= WATER_CAP_M3_PER_MU_YEAR,
        "cap_total_m3_year": cap_total,
        "formula": "LR = ECw / (5×ECe,t − ECw)；V = LR × d_root × A",
        "note": "稳态维持性估算，不是完整水盐运移模型；初始盐分高时两年内不能降到目标值。",
    }


def gypsum_requirement(
    *,
    cec_cmol_kg: float | None,
    esp_percent: float | None,
    target_esp_percent: float = 5.0,
    rho_b: float = 1.54,
    depth_cm: float = 20.0,
) -> dict[str, Any]:
    if cec_cmol_kg is None or esp_percent is None:
        return {
            "status": "refused",
            "reason": "ESP/SAR/CEC 缺失，不能给精确石膏用量；先补测。",
            "missing": ["ESP", "CEC", "SAR"],
        }
    delta = max(0.0, esp_percent - target_esp_percent)
    gr_kg_ha = 0.086 * cec_cmol_kg * delta * rho_b * depth_cm
    return {
        "status": "conditional",
        "GR_kg_ha": round(gr_kg_ha, 1),
        "GR_t_ha": round(gr_kg_ha / 1000, 3),
        "formula": "GR = 0.086 × CEC × ΔESP × ρb × d",
        "note": "简化交换性钠估算；系数与适用边界需按正式文本核对，仅条件性建议。",
    }


def resource_balance(scenario: str = "base") -> dict[str, Any]:
    biochar_t = STRAW_T * STRAW_BIOCHAR_YIELD
    biochar_per_plot_t = 3 * (AREA_PER_PLOT_MU * MU_M2 / 10_000)
    plots_by_biochar = biochar_t / biochar_per_plot_t if biochar_per_plot_t else 0
    manure_per_plot_t = 7.5 * (AREA_PER_PLOT_MU * MU_M2 / 10_000)
    plots_by_manure = MANURE_T / manure_per_plot_t if manure_per_plot_t else 0
    cap = 30 if scenario == "reduced" else WATER_CAP_M3_PER_MU_YEAR
    water_per_plot = cap * AREA_PER_PLOT_MU
    total_water = water_per_plot * len(PLOTS)
    return {
        "straw_t": STRAW_T,
        "biochar_t": round(biochar_t, 1),
        "biochar_yield": STRAW_BIOCHAR_YIELD,
        "biochar_per_plot_t": round(biochar_per_plot_t, 2),
        "plots_covered_by_biochar": round(plots_by_biochar, 2),
        "manure_t": MANURE_T,
        "manure_per_plot_t": round(manure_per_plot_t, 2),
        "plots_covered_by_manure": round(plots_by_manure, 2),
        "water_cap_m3_per_mu_year": cap,
        "water_total_m3_year": round(total_water, 0),
        "resource_gap": {
            "biochar": "不足" if plots_by_biochar + 1e-9 < len(PLOTS) else "足够",
            "manure": "不足" if plots_by_manure + 1e-6 < len(PLOTS) else "足够",
            "water": "受限" if scenario == "reduced" else "刚好到上限",
        },
        "note": "秸秆 80 t 按 30% 产炭率约 24 t；3 t/ha 只够约 3 个地块；不能 5 块均摊。",
    }


def budget_check(scenario: str = "base") -> dict[str, Any]:
    route_costs = {
        "A": [24, 36],
        "B": [36, 50],
        "C": [50, 70],
    }
    return {
        "budget_wan": BUDGET_CNY / 10_000,
        "scenario": scenario,
        "route_cost_range_wan": route_costs,
        "note": "费用为示意/学生模拟；C 50–70 万元/两年可能超过 60 万元预算。",
        "exceeds_budget": {"A": False, "B": False, "C": "可能"},
    }
