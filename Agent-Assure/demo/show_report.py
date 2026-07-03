"""Pretty-print an Agent-Assure JSON grounding report read from stdin.

Usage:
  ground_check.py --draft D --store S --json | python demo/show_report.py

Prints the gate + per-claim verdicts and exits 0 on PASS, 1 otherwise (so the
demo's exit code mirrors the engine's).
"""
import json
import sys

report = json.load(sys.stdin)
print(f"gate: {report['gate']} | score: {report['grounding_score']}")
for claim in report["per_claim"]:
    print(f"  {claim['verdict']:<20} <- {claim['text'][:70]}")
sys.exit(0 if report["gate"] == "PASS" else 1)
