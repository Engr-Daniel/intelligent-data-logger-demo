"""Session isolation, evidence fidelity and live history without paid requests."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.interface import web_service as web


class Block:
    def __init__(self, **data):
        self.data = data

    def model_dump(self):
        return self.data


def response(*blocks):
    return SimpleNamespace(content=[Block(**b) for b in blocks],
                           usage=Block(input_tokens=10, output_tokens=20),
                           model="mock-model", stop_reason="end_turn")


def test_offline_records_real_receipt_and_does_not_contact_api(monkeypatch):
    evidence = {"finding": "Measured state", "measurements": [], "data_quality": {"sufficient": True}}
    tool = Mock(return_value=evidence)
    monkeypatch.setattr(web, "execute_tool", tool)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    session = web.Conversation()
    record = session.ask("Current system status")
    assert record["status"] == "complete"
    assert record["tools"][0]["evidence"] == evidence
    assert record["model"] is None
    assert record["usage"] == []


def test_unknown_offline_question_does_not_invent_inverter_diagnosis(monkeypatch):
    tool = Mock()
    monkeypatch.setattr(web, "execute_tool", tool)
    assert web.Conversation().ask("Tell me a joke")["status"] == "unsupported"
    tool.assert_not_called()


def test_live_followup_receives_history_and_sessions_are_isolated(monkeypatch):
    monkeypatch.setattr(web, "dashboard", lambda: {"timestamp": "2026-11-28 23:55:00+01:00"})
    monkeypatch.setattr(web, "execute_tool", lambda *_: {"finding": "Observed evidence"})
    client = SimpleNamespace(messages=Mock())
    client.messages.create.side_effect = [
        response({"type": "tool_use", "id": "t1", "name": "get_system_status", "input": {"question": "Status?"}}),
        response({"type": "text", "text": "First answer"}),
        response({"type": "text", "text": "Follow-up answer"}),
    ]
    first = web.Conversation()
    record = first.ask("Status?", "live", client)
    assert record["tools"][0]["evidence"]["finding"] == "Observed evidence"
    assert len(record["usage"]) == 2
    first.ask("Explain that", "live", client)
    assert any(m["role"] == "assistant" for m in client.messages.create.call_args.kwargs["messages"][:-1])
    assert web.Conversation().history == []
    assert len(first.turns) == 2
    with pytest.raises(ValueError, match="changing mode"):
        first.ask("Status", "offline")


def test_upstream_error_does_not_leak_secret(monkeypatch):
    monkeypatch.setattr(web, "dashboard", lambda: {"timestamp": "2026-11-28"})
    client = SimpleNamespace(messages=Mock())
    client.messages.create.side_effect = RuntimeError("secret-api-value")
    record = web.Conversation().ask("Status?", "live", client)
    assert record["status"] == "error"
    assert "secret-api-value" not in str(record)


def test_history_committed_only_when_answer_completes(monkeypatch):
    monkeypatch.setattr(web, "dashboard", lambda: {"timestamp": "2026-11-28"})
    monkeypatch.setattr(web, "execute_tool", lambda *_: {})
    client = SimpleNamespace(messages=Mock())
    client.messages.create.return_value = response({"type": "tool_use", "id": "t1", "name": "get_system_status", "input": {"question": "status"}})
    session = web.Conversation()
    assert session.ask("Status", "live", client)["status"] == "round_limit"
    assert session.history == []
    assert client.messages.create.call_count == 6


def test_dashboard_chart_date_does_not_change_snapshot():
    current = web.dashboard()
    past = web.dashboard("2026-09-18")
    assert current["timestamp"] == past["timestamp"]
    assert past["selected_day"] == "2026-09-18"
    assert past["missing_rows"] == 9
    assert any(r["pv_ac_power_w"] is None for r in past["chart"])
    assert "ANTHROPIC_API_KEY" not in str(past)


def test_question_validation_and_session_limit():
    session = web.Conversation()
    for invalid in (None, "", " " , "x" * 2001):
        with pytest.raises(ValueError):
            session.ask(invalid)
    with pytest.raises(ValueError):
        session.ask("Status", "invalid")
    session.turns = [{}] * 20
    with pytest.raises(ValueError, match="20-turn"):
        session.ask("Status")
