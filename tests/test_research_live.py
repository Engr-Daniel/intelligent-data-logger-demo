import json
from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd

from src.research.live import Budget, run_case, score_final


CONFIG={"model":"mock-model","max_output_tokens":700,"max_requests":48,
        "input_usd_per_million":3,"output_usd_per_million":15}


class Block:
    def __init__(self,**kwargs): self.data=kwargs
    def model_dump(self): return self.data


def response(*blocks):
    return SimpleNamespace(content=[Block(**b) for b in blocks],usage=Block(input_tokens=100,output_tokens=50),
                           model="mock-model",stop_reason="end_turn")


def test_live_evidence_is_from_restricted_view_and_no_oracle_in_prompt(monkeypatch):
    from src.research import live
    receipt={"label":"unknown","measurements":{"valid_days":1},"reason":"No history"}
    tool=Mock(return_value=receipt)
    monkeypatch.setattr(live,"diagnose",tool)
    client=SimpleNamespace(messages=Mock())
    client.messages.create.side_effect=[
        response({"type":"tool_use","id":"one","name":"pv_trend","input":{}}),
        response({"type":"text","text":json.dumps({"label":"unknown","explanation":"Only one day", "citations":["valid_days"]})})]
    view=pd.DataFrame({"timestamp":[pd.Timestamp('2026-01-01')],"pv_ac_power_w":[4]})
    record=run_case(client,view,{},"pv_trend","secret-oracle-label",{},CONFIG,Budget(CONFIG))
    assert record["status"]=="complete"
    assert record["tool_selection_correct"]
    assert record["scores"]["label_fidelity"]
    assert not record["scores"]["oracle_correct"]
    assert "secret-oracle-label" not in json.dumps(record)
    assert tool.call_args.args[0] is view


def test_live_budget_blocks_before_request():
    client=SimpleNamespace(messages=Mock())
    view=pd.DataFrame({"timestamp":[pd.Timestamp('2026-01-01')]})
    record=run_case(client,view,{},"alarm","normal",{},CONFIG,Budget(CONFIG,max_usd=0))
    assert record["status"]=="budget_limit"
    client.messages.create.assert_not_called()


def test_invalid_json_and_hallucinated_citation_are_not_credited():
    receipt={"label":"normal","measurements":{"power":3}}
    assert not score_final('```json\n{}\n```',receipt,'normal')["valid_json"]
    scores=score_final(json.dumps({"label":"normal","explanation":"ok","citations":["fabricated"]}),receipt,'normal')
    assert scores["oracle_correct"]
    assert not scores["citation_validity"]


def test_live_failure_redacts_upstream_body():
    client=SimpleNamespace(messages=Mock())
    client.messages.create.side_effect=RuntimeError('private credential content')
    view=pd.DataFrame({"timestamp":[pd.Timestamp('2026-01-01')]})
    record=run_case(client,view,{},"alarm","normal",{},CONFIG,Budget(CONFIG))
    assert record["status"]=="error"
    assert "private credential content" not in json.dumps(record)


def test_workspace_header_is_optional(monkeypatch):
    from src.reasoning.api_config import workspace_headers
    monkeypatch.delenv("ANTHROPIC_WORKSPACE_ID", raising=False)
    assert workspace_headers()=={}
    monkeypatch.setenv("ANTHROPIC_WORKSPACE_ID","wrkspc_test")
    assert workspace_headers()=={"anthropic-workspace-id":"wrkspc_test"}
