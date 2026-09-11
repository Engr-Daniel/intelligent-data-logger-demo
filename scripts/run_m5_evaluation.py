from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.evaluation.runner import write_report

if __name__ == "__main__":
    json_path, md_path = write_report()
    print(f"M5 evaluation complete: {json_path}")
    print(f"Reviewer summary: {md_path}")
