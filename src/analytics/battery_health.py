from __future__ import annotations

import numpy as np
import pandas as pd


def detect_battery_capacity_decline(
    df: pd.DataFrame,
    interval_minutes: int,
    nominal_usable_capacity_kwh: float,
    charge_efficiency: float,
    discharge_efficiency: float,
    decline_threshold_pct: float = 3.0,
) -> dict:
    """Estimate longitudinal usable-capacity change from observable SOC and power flows.

    The estimator deliberately does NOT use ``battery_usable_capacity_wh`` or
    ``battery_stored_energy_wh``.  For intervals with a meaningful SOC change,
    effective capacity is inferred from energy moved into/out of the battery
    divided by the corresponding fractional SOC change. Daily medians make the
    controlled demo estimate robust to interval-level noise.

    This is a synthetic-demo diagnostic, not a field-validated SOH estimator.
    """
    required = ["timestamp", "battery_soc_pct", "battery_charge_w", "battery_discharge_w"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return _insufficient(f"Missing required observed battery fields: {missing}")

    w = df[required].copy()
    w["timestamp"] = pd.to_datetime(w["timestamp"])
    w = w.sort_values("timestamp")
    dt_h = interval_minutes / 60.0
    dsoc = w["battery_soc_pct"].diff() / 100.0
    net_stored_wh = (
        w["battery_charge_w"] * dt_h * charge_efficiency
        - w["battery_discharge_w"] * dt_h / discharge_efficiency
    )

    # Require a measurable SOC movement and agreement between flow and SOC direction.
    direction_ok = (np.sign(net_stored_wh) == np.sign(dsoc)) & (net_stored_wh.abs() > 1e-9)
    meaningful = dsoc.abs() >= 0.002  # >= 0.2 percentage-point SOC movement
    estimate_wh = net_stored_wh / dsoc
    nominal_wh = nominal_usable_capacity_kwh * 1000.0
    plausible = estimate_wh.between(0.5 * nominal_wh, 1.5 * nominal_wh)
    valid = direction_ok & meaningful & plausible & estimate_wh.notna()
    w["capacity_estimate_wh"] = estimate_wh.where(valid)
    w["date"] = w["timestamp"].dt.date

    daily = w.groupby("date")["capacity_estimate_wh"].agg(["median", "count"])
    daily = daily[daily["count"] >= 20].dropna()
    if len(daily) < 28:
        return _insufficient("Too few days contain sufficient SOC/power transitions for a longitudinal capacity estimate.")

    edge_days = min(14, max(7, len(daily) // 5))
    early = float(daily.iloc[:edge_days]["median"].median())
    late = float(daily.iloc[-edge_days:]["median"].median())
    decline_pct = 100.0 * (1.0 - late / early) if early > 0 else np.nan

    # Localize the onset from observations only: first 3-day rolling median that
    # is >0.2% below the early baseline. This is not given the injected start date.
    rolling = daily["median"].rolling(3, min_periods=3).median()
    onset_candidates = rolling[rolling <= early * 0.998]
    onset_date = onset_candidates.index[0] if len(onset_candidates) else daily.index[0]
    end_date = daily.index[-1]
    tz = w["timestamp"].dt.tz
    start_ts = pd.Timestamp(onset_date)
    end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(minutes=interval_minutes)
    if tz is not None:
        start_ts = start_ts.tz_localize(tz)
        end_ts = end_ts.tz_localize(tz)

    detected = bool(np.isfinite(decline_pct) and decline_pct >= decline_threshold_pct)
    candidate = "battery_capacity_degradation" if detected else "no_material_battery_capacity_decline"
    confidence = "high" if detected and len(daily) >= 60 else "medium"
    finding = (
        f"Observed SOC and charge/discharge flows imply a {decline_pct:.1f}% reduction in effective usable battery capacity over the observation period."
        if detected
        else f"Observed SOC and charge/discharge flows do not show a material usable-capacity decline above the {decline_threshold_pct:.1f}% demo threshold."
    )
    return {
        "finding": finding,
        "candidate_cause": candidate,
        "confidence": confidence,
        "data_window": {"start": start_ts.isoformat(), "end": end_ts.isoformat()},
        "measurements": [
            {"name": "early_estimated_usable_capacity_wh", "value": round(early, 1), "unit": "Wh"},
            {"name": "late_estimated_usable_capacity_wh", "value": round(late, 1), "unit": "Wh"},
            {"name": "estimated_capacity_decline_pct", "value": round(float(decline_pct), 2), "unit": "%"},
            {"name": "days_with_capacity_estimates", "value": int(len(daily)), "unit": "days"},
            {"name": "valid_transition_estimates", "value": int(w["capacity_estimate_wh"].notna().sum()), "unit": "transitions"},
        ],
        "alternatives_checked": [
            {"alternative": "single-interval SOC fluctuation", "result": "reduced by daily-median aggregation across many transitions"},
            {"alternative": "latent simulator capacity state", "result": "not used by this diagnostic"},
            {"alternative": "insufficient cycling evidence", "result": "not supported" if len(daily) >= 28 else "possible"},
        ],
        "data_quality": {"sufficient": True, "warnings": ["Controlled-demo capacity estimator; not field-validated battery SOH inference."]},
        "assumptions": {
            "interval_minutes": interval_minutes,
            "charge_efficiency": charge_efficiency,
            "discharge_efficiency": discharge_efficiency,
            "nominal_usable_capacity_kwh_used_only_for_plausibility_filter": nominal_usable_capacity_kwh,
            "minimum_soc_change_pct_points": 0.2,
            "decline_threshold_pct": decline_threshold_pct,
        },
    }


def _insufficient(message: str) -> dict:
    return {
        "finding": message,
        "candidate_cause": None,
        "confidence": "low",
        "measurements": [],
        "alternatives_checked": [],
        "data_quality": {"sufficient": False, "warnings": [message]},
        "assumptions": {},
    }
