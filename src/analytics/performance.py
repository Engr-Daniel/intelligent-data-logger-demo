from __future__ import annotations

import numpy as np
import pandas as pd


def performance_ratio(df: pd.DataFrame, pv_kwp: float, inverter_rating_w: float | None = None, minimum_irradiance_wm2: float = 200.0) -> dict:
    """Observed AC performance normalized for irradiance and module-temperature effects.

    This deliberately does not use the simulator's latent performance factor.
    """
    required = {"timestamp", "pv_ac_power_w", "irradiance_wm2", "ambient_temp_c"}
    missing = sorted(required - set(df.columns))
    if missing:
        return {"status": "INSUFFICIENT_DATA", "data_quality": {"sufficient": False, "warnings": [f"Missing columns: {', '.join(missing)}"]}}
    x = df[list(required)].copy()
    x["timestamp"] = pd.to_datetime(x["timestamp"])
    x = x.dropna()
    x = x[x["irradiance_wm2"] >= minimum_irradiance_wm2]
    clipping_excluded = 0
    if inverter_rating_w is not None:
        before = len(x)
        x = x[x["pv_ac_power_w"] < 0.98 * inverter_rating_w]
        clipping_excluded = before - len(x)
    if len(x) < 24:
        return {"status": "INSUFFICIENT_DATA", "data_quality": {"sufficient": False, "warnings": ["Too few valid daylight samples"]}}
    # Same temperature coefficient used by the synthetic PV model; this is a configured/demo assumption.
    temp_factor = 1 - 0.004 * np.maximum(x["ambient_temp_c"].to_numpy() - 25.0, 0)
    expected_dc_w = pv_kwp * 1000 * (x["irradiance_wm2"].to_numpy() / 1000) * temp_factor
    # Nominal inverter conversion is intentionally not divided out: this is an AC-side normalized yield index.
    ratio = np.divide(x["pv_ac_power_w"].to_numpy(), expected_dc_w, out=np.full(len(x), np.nan), where=expected_dc_w > 0)
    x["observed_ac_performance_ratio"] = ratio
    daily = x.groupby(x["timestamp"].dt.floor("D"))["observed_ac_performance_ratio"].median().dropna()
    if len(daily) < 14:
        return {"status": "INSUFFICIENT_DATA", "data_quality": {"sufficient": False, "warnings": ["Fewer than 14 valid daily performance estimates"]}}
    return {
        "status": "PASS",
        "median_ac_performance_ratio": round(float(daily.median()), 4),
        "daily": daily,
        "valid_samples": int(len(x)),
        "valid_days": int(len(daily)),
        "data_quality": {"sufficient": True, "warnings": []},
        "assumptions": {"temperature_coefficient_per_c": -0.004, "minimum_irradiance_wm2": minimum_irradiance_wm2, "clipping_excluded_samples": clipping_excluded},
    }


def detect_gradual_performance_decline(df: pd.DataFrame, pv_kwp: float, inverter_rating_w: float | None = None, minimum_decline_pct: float = 4.0) -> dict:
    """Detect a multi-week decline from observed telemetry, without latent simulator state."""
    pr = performance_ratio(df, pv_kwp, inverter_rating_w)
    if pr.get("status") != "PASS":
        return {
            "finding": "There is insufficient observed telemetry to evaluate a gradual PV performance trend.",
            "candidate_cause": None,
            "confidence": "low",
            "measurements": [],
            "alternatives_checked": [],
            "data_quality": pr.get("data_quality", {"sufficient": False}),
        }
    daily: pd.Series = pr["daily"]
    n = max(7, min(14, len(daily) // 4))
    early = float(daily.iloc[:n].median())
    late = float(daily.iloc[-n:].median())
    decline_pct = max(0.0, (early - late) / early * 100) if early > 0 else 0.0
    # Robust trend direction using a linear fit to daily medians; magnitude is reported separately via early/late medians.
    slope_per_day = float(np.polyfit(np.arange(len(daily), dtype=float), daily.to_numpy(), 1)[0])
    detected = decline_pct >= minimum_decline_pct and slope_per_day < 0
    return {
        "finding": (
            "Observed irradiance- and temperature-normalized PV performance shows a sustained downward multi-week trend."
            if detected else "Observed normalized PV performance does not show a material sustained decline."
        ),
        "candidate_cause": "gradual_pv_performance_decline" if detected else "no_material_gradual_decline",
        "confidence": "high" if detected and decline_pct >= minimum_decline_pct * 1.5 else "medium",
        "data_window": {"start": daily.index.min().isoformat(), "end": daily.index.max().isoformat()},
        "measurements": [
            {"name": "early_period_median_performance_ratio", "value": round(early, 4), "unit": "ratio"},
            {"name": "late_period_median_performance_ratio", "value": round(late, 4), "unit": "ratio"},
            {"name": "normalized_performance_decline_pct", "value": round(decline_pct, 2), "unit": "%"},
            {"name": "daily_trend_slope", "value": round(slope_per_day, 7), "unit": "ratio/day"},
            {"name": "valid_days", "value": int(len(daily)), "unit": "days"},
        ],
        "alternatives_checked": [
            {"cause": "lower_irradiance", "supported": False, "evidence": "Performance is normalized by measured irradiance."},
            {"cause": "ambient_temperature_variation", "supported": False, "evidence": "Expected PV output is temperature-adjusted."},
            {"cause": "inverter_clipping", "supported": False, "evidence": {"excluded_clipping_samples": pr["assumptions"].get("clipping_excluded_samples", 0)}},
            {"cause": "missing_data", "supported": not pr["data_quality"]["sufficient"], "evidence": {"valid_days": int(len(daily))}},
        ],
        "data_quality": pr["data_quality"],
        "assumptions": pr["assumptions"] | {"minimum_decline_pct": minimum_decline_pct},
    }
