"""M5 evaluation package.

Ground truth is intentionally imported only inside this package. Operational
analytics/reasoning modules must never depend on it.
"""

from .runner import run_m5_evaluation

__all__ = ["run_m5_evaluation"]
