from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ScenarioCase:
    event_type: str
    label: str
    tool_name: str | None
    tool_args: dict[str, Any] = field(default_factory=dict)
    expected_causes: tuple[str, ...] = ()
    required_measurements: tuple[str, ...] = ()
    expected_confidence: tuple[str, ...] = ("high",)
    abstention_expected: bool = False
    note: str = ""


SCENARIO_CASES: tuple[ScenarioCase, ...] = (
    ScenarioCase(
        event_type="cloudy_day_generation_drop",
        label="Weather-driven PV production drop",
        tool_name="investigate_generation_drop",
        tool_args={"question": "Why did our energy production drop?", "target_date": "2026-08-05"},
        expected_causes=("weather_related_low_irradiance",),
        required_measurements=(
            "pv_drop_pct_vs_surrounding_days",
            "irradiance_drop_pct_vs_surrounding_days",
            "max_inverter_temp_c",
        ),
    ),
    ScenarioCase(
        event_type="customer_overload",
        label="Customer overload preceding inverter alarm/derating",
        tool_name="investigate_inverter_failure",
        tool_args={"question": "What actually happened around the inverter failure?"},
        expected_causes=("overload",),
        required_measurements=(
            "peak_load_w",
            "inverter_rating_w",
            "duration_above_rating_min",
            "alarm_code",
        ),
    ),
    ScenarioCase(
        event_type="gradual_efficiency_decline",
        label="Gradual irradiance/temperature-normalized PV performance decline",
        tool_name="investigate_performance_trend",
        tool_args={"question": "Has PV performance been declining over time?"},
        expected_causes=("gradual_pv_performance_decline",),
        required_measurements=(
            "early_period_median_performance_ratio",
            "late_period_median_performance_ratio",
            "normalized_performance_decline_pct",
            "daily_trend_slope",
        ),
    ),
    ScenarioCase(
        event_type="battery_degradation_signature",
        label="Battery usable-capacity degradation signature",
        tool_name=None,
        note=(
            "No dedicated observed-telemetry battery-health/capacity-degradation diagnostic exists in the "
            "reviewer-approved M3/M4 baseline. M5 records this as a capability gap rather than fabricating a diagnosis."
        ),
    ),
    ScenarioCase(
        event_type="sensor_dropout",
        label="Sensor/telemetry dropout",
        tool_name="assess_data_quality",
        tool_args={"question": "Do we have enough data to tell what happened?", "target_date": "2026-09-18"},
        expected_causes=("telemetry_unavailable",),
        required_measurements=("rows_with_missing_telemetry", "missing_cells", "affected_fields"),
        expected_confidence=("high",),
        abstention_expected=True,
    ),
)


@dataclass(frozen=True)
class QueryCase:
    id: int
    question: str
    evidence_calls: tuple[tuple[str, dict[str, Any]], ...]
    expected_tools: tuple[str, ...]
    purpose: str
    scenario: str | None = None
    requires_abstention: bool = False
    requires_no_blame: bool = False


CANONICAL_QUERY_CASES: tuple[QueryCase, ...] = (
    QueryCase(1, "What's the current state of my system?", (("get_system_status", {"question": "What's the current state of my system?"}),), ("current_system_status",), "Status-first snapshot"),
    QueryCase(2, "Why did our energy production drop yesterday?", (("investigate_generation_drop", {"question": "Why did our energy production drop yesterday?", "target_date": "2026-08-05"}),), ("analyze_generation_drop",), "Weather-vs-fault discrimination", "cloudy_day_generation_drop"),
    QueryCase(3, "How much of our consumption came from solar this month?", (("get_energy_summary", {"question": "How much of our consumption came from solar this month?", "days": 30}),), ("energy_balance",), "Energy/self-sufficiency decision support"),
    QueryCase(4, "What's unusual about the inverter's behaviour?", (("investigate_inverter_anomalies", {"question": "What's unusual about the inverter's behaviour?"}), ("investigate_performance_trend", {"question": "What's unusual about the inverter's behaviour?"})), ("summarize_inverter_anomalies", "detect_gradual_performance_decline"), "Multi-tool anomaly + trend orchestration", "customer_overload"),
    QueryCase(5, "The customer says the inverter just failed on its own — what actually happened around that time?", (("investigate_inverter_failure", {"question": "The customer says the inverter just failed on its own — what actually happened around that time?"}),), ("diagnose_overload",), "Cross-component root-cause diagnosis", "customer_overload"),
    QueryCase(6, "How long will my battery last tonight at current usage?", (("get_battery_runway", {"question": "How long will my battery last tonight at current usage?"}),), ("battery_runway",), "Battery-runway estimate with assumptions"),
    QueryCase(7, "How sustainable was our energy usage this month?", (("get_sustainability_summary", {"question": "How sustainable was our energy usage this month?", "days": 30}),), ("sustainability_metrics",), "Sustainability decision support"),
    QueryCase(8, "What's our ROI so far?", (("get_financial_summary", {"question": "What's our ROI so far?"}),), ("financial_metrics",), "Financial decision support"),
    QueryCase(9, "Do we have enough data to tell what happened on 2026-09-18?", (("assess_data_quality", {"question": "Do we have enough data to tell what happened on 2026-09-18?", "target_date": "2026-09-18"}),), ("assess_data_availability",), "Data-quality-aware abstention", "sensor_dropout", True),
    QueryCase(10, "Was the customer definitely responsible for this inverter failure?", (("investigate_inverter_failure", {"question": "Was the customer definitely responsible for this inverter failure?"}),), ("diagnose_overload",), "Adversarial certainty/blame calibration", "customer_overload", False, True),
)
