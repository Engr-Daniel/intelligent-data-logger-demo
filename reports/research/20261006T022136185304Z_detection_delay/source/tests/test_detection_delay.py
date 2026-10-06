"""Boundary cases for the exploratory timing scorer and existing access filter."""
import unittest
import pandas as pd
from scripts.analyze_detection_delay import scheduled_days, alert_days, outcome, reference_day
from src.research.policy import restrict


class DetectionDelayTests(unittest.TestCase):
    def test_phases_partition_days_without_forced_final_check(self):
        all_days = [d for p in range(30) for d in scheduled_days(30, p)]
        self.assertEqual(sorted(all_days), list(range(14, 61)))
        self.assertEqual(scheduled_days(30, 0), [14, 44])

    def test_persistence_uses_only_scheduled_checks_and_unknown_resets(self):
        labels = {d: 'pv_decline' for d in range(14, 61)}
        self.assertEqual(alert_days(labels, 7, 0, 3)[0][0], 28)
        labels[21] = 'unknown'
        self.assertEqual(alert_days(labels, 7, 0, 3)[0][0], 42)
        self.assertEqual(alert_days(labels, 30, 0, 3)[0], [])

    def test_pre_reference_alert_does_not_replace_later_detection(self):
        row = outcome([18, 33], 30)
        self.assertEqual(row['pre_reference_alert'], 1)
        self.assertEqual(row['delay_days'], 3)
        self.assertEqual(row['waiting_days'], 3)

    def test_miss_and_below_threshold_are_distinct(self):
        self.assertEqual(outcome([18], 30)['waiting_days'], 31)
        self.assertEqual(outcome([], 60)['waiting_days'], 1)
        self.assertIsNone(outcome([18], None)['detected'])
        self.assertIsNone(reference_day(.035))
        self.assertEqual(reference_day(.10), 31)

    def test_future_data_never_reaches_policy(self):
        times = pd.date_range('2026-01-01', periods=4, freq='12h', tz='Africa/Lagos')
        frame = pd.DataFrame({'timestamp': times, 'pv_ac_power_w': [1, 2, 999, 999], 'secret_oracle': ['x']*4})
        view = restrict(frame, 'full_inverter', times[1])
        self.assertEqual(view.pv_ac_power_w.tolist(), [1, 2])
        self.assertNotIn('secret_oracle', view)


if __name__ == '__main__':
    unittest.main()
