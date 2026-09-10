from __future__ import annotations

import sys
import types
from types import SimpleNamespace

from src.reasoning import agent


class _FakeMessages:
    def __init__(self):
        self.calls = 0
        self.tool_names_seen = []

    def create(self, **kwargs):
        self.calls += 1
        self.tool_names_seen.append({tool["name"] for tool in kwargs.get("tools", [])})
        if self.calls == 1:
            return SimpleNamespace(
                content=[
                    SimpleNamespace(
                        type="tool_use",
                        id="toolu_demo",
                        name="investigate_generation_drop",
                        input={"question": "Why did generation drop?", "target_date": "2026-08-05"},
                    )
                ]
            )
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text="Weather-related low irradiance is the strongest supported cause.")]
        )


class _FakeAnthropicClient:
    last_messages = None

    def __init__(self, api_key):
        self.messages = _FakeMessages()
        _FakeAnthropicClient.last_messages = self.messages


def test_claude_tool_loop_executes_selected_tool_and_returns_final_text(monkeypatch):
    fake_module = types.ModuleType("anthropic")
    fake_module.Anthropic = _FakeAnthropicClient
    monkeypatch.setitem(sys.modules, "anthropic", fake_module)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "test-model")

    result = agent.answer("Why did generation drop on 2026-08-05?")

    assert "Weather-related" in result
    messages = _FakeAnthropicClient.last_messages
    assert messages is not None
    assert messages.calls == 2
    assert any({"investigate_inverter_failure", "investigate_generation_drop"}.issubset(names) for names in messages.tool_names_seen)


def test_fallback_honors_explicit_valid_date(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = agent.fallback_answer("Why did generation drop on 2026-08-06?")

    # 2026-08-06 is an ordinary day in the demo dataset. If the fallback
    # ignored the date it would auto-select the cloudy anomaly instead.
    assert "does not show a material PV production drop" in result
    assert "lower solar irradiance" not in result


def test_fallback_without_date_retains_anomaly_auto_selection(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = agent.fallback_answer("Why did our solar generation drop?")

    assert "lower solar irradiance" in result


def test_fallback_out_of_range_date_reports_no_data(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = agent.fallback_answer("Why did generation drop on 2025-01-01?")

    assert "No daytime telemetry is available for 2025-01-01" in result
    assert "lower solar irradiance" not in result
