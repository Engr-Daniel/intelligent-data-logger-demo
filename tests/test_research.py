import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.research.simulation import EPISODES, generate, corrupt
from src.research.policy import restrict, diagnose, INVERTER
from src.research.reporting import metrics, summarize

PROTOCOL = json.loads((Path(__file__).resolve().parents[1]/"config/research_protocol.json").read_text())


@pytest.mark.parametrize("episode", [e[0] for e in EPISODES])
def test_all_episodes_have_physical_balance_and_no_oracle_columns(episode):
    df, static, oracle, physical = generate(100, episode)
    assert physical["passed"]
    assert df.timestamp.is_unique
    assert len(df) == 5760
    assert not {"label", "episode", "seed", "performance_factor", "usable_capacity_wh"} & set(df.columns)
    assert set(static) == {"pv_kwp", "inverter_rating_w", "interval_minutes"}
    assert set(df.inverter_alarm.dropna().unique()) <= {0, 1}


def test_access_boundary_removes_future_latent_and_external_channels():
    df, static, _, _ = generate(101, "day_weather")
    df["oracle_label"] = "do not read"
    end = df.timestamp.iloc[-49]
    view = restrict(df, "recent_inverter", end)
    assert list(view.columns) == list(INVERTER)
    assert len(view) == 96
    assert view.timestamp.max() == end
    assert view.timestamp.min() > end-pd.Timedelta(days=1)
    assert "irradiance_wm2" not in view
    with pytest.raises(ValueError): restrict(df, "invalid", end)


def test_generation_and_corruption_are_reproducible_without_mutation():
    a, _, _, _ = generate(100, "day_normal")
    b, _, _, _ = generate(100, "day_normal")
    pd.testing.assert_frame_equal(a,b)
    original = a.copy(deep=True)
    x = corrupt(a, 55, .03, .01)
    y = corrupt(a, 55, .03, .01)
    pd.testing.assert_frame_equal(x,y)
    pd.testing.assert_frame_equal(a,original)
    assert not x.equals(a)


def test_missing_and_ambiguous_evidence_require_abstention():
    for episode in ("day_missing", "alarm_unexplained"):
        df, static, oracle, _ = generate(100, episode)
        result = diagnose(restrict(df, "full_cross", oracle["query_time"]), static, oracle["task"], PROTOCOL["thresholds"])
        assert result["label"] == "unknown"
        assert oracle["label"] == "unknown"


def test_inverter_alarm_codes_do_not_reveal_injected_cause():
    for episode in ("alarm_overload", "alarm_thermal", "alarm_unexplained"):
        df, *_ = generate(100, episode)
        assert set(df.inverter_alarm.unique()) == {0,1}


def test_abstention_is_not_credited_as_correct_identifiable_diagnosis():
    rows = pd.DataFrame([{"expected":"normal", "predicted":"unknown", "correct":False},
                         {"expected":"unknown", "predicted":"unknown", "correct":True}])
    result = metrics(rows)
    assert result["diagnostic_accuracy"] == 0
    assert result["coverage"] == 0
    assert np.isnan(result["selective_accuracy"])
    assert result["correct_abstention"] == 1
    assert result["normal_false_positive_rate"] == 0


def test_cluster_effects_are_paired_and_do_not_count_episodes_as_installations():
    data=[]
    for seed in [100,101,102]:
        for stress in PROTOCOL["stress_levels"]:
            for condition in PROTOCOL["conditions"]:
                for _ in range(4):
                    correct = condition == "full_cross"
                    data.append(dict(seed=seed,stress=stress,condition=condition,expected="normal",
                                     predicted="normal" if correct else "unknown",correct=correct))
    summary,effects,clusters=summarize(pd.DataFrame(data),PROTOCOL)
    assert set(summary.installations)=={3}
    assert set(summary.cases)=={12}
    assert set(effects.clusters)=={3}
    assert set(effects.difference)=={1.0}
    assert set(effects.ci_low)=={1.0}


def test_development_and_evaluation_seeds_are_disjoint():
    assert not set(PROTOCOL["development_seeds"]) & set(PROTOCOL["evaluation_seeds"])
