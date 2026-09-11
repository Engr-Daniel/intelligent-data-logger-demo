from __future__ import annotations

from src.evaluation.cases import ScenarioCase, CANONICAL_QUERY_CASES, QueryCase

# M5's rubric/dimensions remain unchanged. M6 changes only the operational
# capability used to produce evidence for the two gaps exposed by M5.
M6_SCENARIO_CASES: tuple[ScenarioCase, ...] = (
    ScenarioCase(
        event_type="cloudy_day_generation_drop", label="Weather-driven PV production drop",
        tool_name="investigate_generation_drop",
        tool_args={"question":"Why did our energy production drop?","target_date":"2026-08-05"},
        expected_causes=("weather_related_low_irradiance",),
        required_measurements=("pv_drop_pct_vs_surrounding_days","irradiance_drop_pct_vs_surrounding_days","max_inverter_temp_c"),
    ),
    ScenarioCase(
        event_type="customer_overload", label="Customer overload preceding inverter alarm/derating",
        tool_name="investigate_inverter_failure",
        tool_args={"question":"What actually happened around the inverter failure?"},
        expected_causes=("overload",),
        required_measurements=("peak_load_w","inverter_rating_w","duration_above_rating_min","alarm_code"),
    ),
    ScenarioCase(
        event_type="gradual_efficiency_decline", label="Gradual irradiance/temperature-normalized PV performance decline",
        tool_name="investigate_performance_trend",
        tool_args={"question":"Has PV performance been declining over time?"},
        expected_causes=("gradual_pv_performance_decline",),
        required_measurements=("early_period_median_performance_ratio","late_period_median_performance_ratio","normalized_performance_decline_pct","daily_trend_slope"),
    ),
    ScenarioCase(
        event_type="battery_degradation_signature", label="Battery usable-capacity degradation signature",
        tool_name="investigate_battery_health",
        tool_args={"question":"Is the battery's usable capacity degrading over time?"},
        expected_causes=("battery_capacity_degradation",),
        required_measurements=("early_estimated_usable_capacity_wh","late_estimated_usable_capacity_wh","estimated_capacity_decline_pct","valid_transition_estimates"),
        expected_confidence=("high","medium"),
        note="M6 estimates capacity change from observed SOC and charge/discharge flows; latent simulator capacity is not an input.",
    ),
    ScenarioCase(
        event_type="sensor_dropout", label="Sensor/telemetry dropout",
        tool_name="investigate_data_gap",
        tool_args={"question":"Do we have enough data to tell what happened?","target_date":"2026-09-18"},
        expected_causes=("telemetry_unavailable",),
        required_measurements=("rows_with_missing_telemetry","missing_cells","affected_fields","gap_start","gap_end","gap_duration_minutes"),
        expected_confidence=("high",), abstention_expected=True,
        note="M6 localizes the missing interval from observed missingness and cadence, without consulting ground truth.",
    ),
)

# Keep the ten canonical questions, but route the data-quality question through
# the refined interval-localization capability. Other query contracts are frozen.
M6_QUERY_CASES: tuple[QueryCase, ...] = tuple(
    QueryCase(
        c.id, c.question,
        (("investigate_data_gap", {"question": c.question, "target_date": "2026-09-18"}),) if c.id == 9 else c.evidence_calls,
        ("localize_data_unavailability",) if c.id == 9 else c.expected_tools,
        c.purpose, c.scenario, c.requires_abstention, c.requires_no_blame,
    )
    for c in CANONICAL_QUERY_CASES
)
