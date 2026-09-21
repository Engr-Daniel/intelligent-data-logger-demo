# Local interface validation — 21 September 2026

The status-first browser interface was checked locally against the existing synthetic
dataset. This is software/interface validation, not a new research evaluation.

| Check | Result |
|---|---|
| Full regression suite, including seven new interface tests | 87 passed in 252.05 seconds |
| HTTP snapshot and offline grid-outage investigation | PASS |
| Separate sessions, reset and evidence JSON export | PASS |
| Rejection of cross-origin mutation requests | PASS |
| Browser chart date change preserves latest status timestamp | PASS |
| Browser missing-data question and expandable insufficient-data evidence | PASS |
| Browser export contains the executed tool's evidence | PASS |
| Unsupported offline question avoids an unrelated inverter diagnosis | PASS |
| Desktop and 390-pixel mobile layouts | Inspected; no horizontal page overflow |
| Browser JavaScript errors during walkthrough | None |
| Claude follow-up history, round limits and error redaction | PASS with mocked API responses |
| Real Claude requests | Not run; zero API requests for these checks |

Run `python scripts/serve_dashboard.py` and open `http://127.0.0.1:8501`.
The interface defaults to offline mode and labels the dataset as synthetic. Live-mode
answers, latency, cost and quality still require the planned live conversational pilot.
