import pandas as pd

from src.analytics.battery import battery_runway
from src.analytics.energy_balance import instantaneous_balance_residual_w
from src.analytics.financial import financial_metrics
from src.analytics.root_cause import diagnose_overload
from src.generator.simulate import load_config, simulate


def test_generator_contains_overload_alarm():
    df, gt = simulate(load_config())
    assert (df["inverter_alarm_code"] == "OVERLOAD_02").any()
    assert gt["events"][0]["event_type"] == "customer_overload"


def test_overload_is_diagnosed():
    cfg = load_config()
    df, _ = simulate(cfg)
    result = diagnose_overload(df, cfg["installation"]["inverter_rating_w"])
    assert result["candidate_cause"] == "overload"
    assert result["confidence"] == "high"


def test_alternative_causes_are_computed_with_evidence():
    cfg = load_config()
    df, _ = simulate(cfg)
    result = diagnose_overload(df, cfg["installation"]["inverter_rating_w"])
    alternatives = {item["cause"]: item for item in result["alternatives_checked"]}
    assert alternatives["grid_outage"]["supported"] is False
    assert "grid_available_fraction" in alternatives["grid_outage"]["evidence"]
    assert alternatives["weather_related_generation_drop_only"]["supported"] is False
    assert "median_irradiance_wm2" in alternatives["weather_related_generation_drop_only"]["evidence"]


def test_power_balance_invariant_default_scenario():
    df, _ = simulate(load_config())
    assert instantaneous_balance_residual_w(df).abs().max() < 1e-6


def test_power_balance_invariant_with_daytime_derate():
    cfg = load_config()
    daytime_overload = pd.Timestamp("2026-08-08 13:00", tz=cfg["installation"]["timezone"])
    df, _ = simulate(cfg, overload_start=daytime_overload)
    derated = df[df["inverter_operating_state"] == "derated"]
    assert not derated.empty
    assert derated["pv_ac_power_w"].max() > 0  # proves this regression test exercises daytime PV derating
    assert instantaneous_balance_residual_w(df).abs().max() < 1e-6


def test_soc_and_battery_power_bounds():
    cfg = load_config()
    df, _ = simulate(cfg)
    inst = cfg["installation"]
    assert df["battery_soc_pct"].between(inst["battery_soc_min_pct"] - 1e-9, inst["battery_soc_max_pct"] + 1e-9).all()
    assert (df["battery_charge_w"] <= inst["battery_max_charge_w"] + 1e-9).all()
    assert (df["battery_discharge_w"] <= inst["battery_max_discharge_w"] + 1e-9).all()


def test_battery_runway_exposes_assumptions():
    result = battery_runway(60, 9.0, 1000, 10)
    assert result["estimated_runway_hours"] == 4.5
    assert result["assumptions"]["load_assumed_constant"] is True


def test_financial_metrics_distinguish_roi_and_payback():
    result = financial_metrics(1000, 200, 1_000_000, period_days=365)
    assert result["simple_roi_pct"] == 20.0
    assert result["simple_payback_years"] == 5.0
