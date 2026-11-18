import json
from pathlib import Path

from engine.calc import (
    soil_mass,
    material_need,
    leaching,
    gypsum_requirement,
    resource_balance,
)
from engine.rules import diagnose_all, qc
from engine.routes import route_compare
from engine.report import write_report


def test_base_diagnosis():
    data = diagnose_all()
    assert len(data["plots"]) == 5
    s04 = next(p for p in data["plots"] if p["id"] == "S04")
    assert s04["salt_class"] == "中度"
    assert s04["recommendation"] == "先排水"
    assert "ESP" in s04["missing"]
    assert "R05" in s04["not_evaluable_rule_ids"]


def test_ec_method_missing_blocks_salinity_class():
    data = diagnose_all({"S04": {"ec_method": "EC1:5"}})
    s04 = next(p for p in data["plots"] if p["id"] == "S04")
    statuses = {r["rule_id"]: r["status"] for r in s04["rule_results"]}
    assert statuses["R01"] == "not_evaluable"
    assert statuses["R02"] == "not_evaluable"


def test_same_ece_different_drainage():
    base = diagnose_all()
    altered = diagnose_all({"S02": {"drainage": "较差", "drainage_key": "poor"}})
    s02_base = next(p for p in base["plots"] if p["id"] == "S02")
    s02_alt = next(p for p in altered["plots"] if p["id"] == "S02")
    assert s02_alt["ece"] == s02_base["ece"]
    assert s02_base["recommendation"] == "A/B"
    assert s02_alt["recommendation"] == "先排水"


def test_sodicity_missing_and_gypsum_refused():
    data = diagnose_all()
    s05 = next(p for p in data["plots"] if p["id"] == "S05")
    r05 = next(r for r in s05["rule_results"] if r["rule_id"] == "R05")
    assert r05["status"] == "not_evaluable"
    result = gypsum_requirement(cec_cmol_kg=None, esp_percent=None)
    assert result["status"] == "refused"


def test_gypsum_conditional_formula():
    result = gypsum_requirement(cec_cmol_kg=20, esp_percent=20, target_esp_percent=5)
    assert result["status"] == "conditional"
    assert abs(result["GR_kg_ha"] - 794.6) < 0.2


def test_s04_mass_and_per_mu():
    mass = soil_mass("S04")
    assert mass["M_t"] == 8213.3
    assert mass["per_mu_t"] == 205.3


def test_material_conversion():
    need = material_need("S03", rate_t_per_ha=3.0, raw_to_product_yield=0.3)
    assert need["product_t"] == 8.0
    assert abs(need["raw_material_t"] - 26.67) < 0.02


def test_leaching_cap():
    water = leaching("S04")
    assert abs(water["LR"] - 0.0684) < 0.0001
    assert water["per_mu_m3_year"] == 27.4
    assert water["within_cap"] is True


def test_resources_base_and_reduced():
    base = resource_balance("base")
    assert base["biochar_t"] == 24.0
    assert base["plots_covered_by_biochar"] == 3.0
    assert base["plots_covered_by_manure"] == 5.0
    assert base["resource_gap"]["biochar"] == "不足"
    reduced = resource_balance("reduced")
    assert reduced["water_cap_m3_per_mu_year"] == 30
    assert reduced["resource_gap"]["water"] == "受限"


def test_routes_and_budget():
    base = route_compare("base")
    assert len(base["routes"]) == 3
    assert base["budget"]["route_cost_range_wan"]["C"] == [50, 70]
    reduced = route_compare("reduced")
    b = next(r for r in reduced["routes"] if r["id"] == "B")
    assert b["suitability"] == "条件性"
    assert "淋洗受限" in b["scenario_tag"]


def test_qc_negative_and_unit_error():
    bad = [{"id": "X01", "ph": 12.5, "ece": -1, "om": 10, "bd": 1.4, "emergence": 80}]
    result = qc(bad, ec_method="EC1:5")
    assert result["passed"] is False
    issues = {e["field"] for e in result["errors"]}
    assert {"ph", "ece", "ec_method"} <= issues


def test_report_written():
    result = write_report("two_year_plan")
    path = Path(result["path"])
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "两年" in text
    assert "ESP" in text
    assert "监测" in text
    assert "教学模拟" in text
