"""Build the (premise, hypothesis, gold) set for the MiniCheck/HHEM diagnostic.

NOT product code. Nothing here is imported by the gate; this lives outside
Agent-Assure/ on purpose so the plugin's install surface stays clean.

Three populations, kept separate because they answer different questions:

  gold52   — the 38 entailment-shaped rows of the ratified corpus. Gold is
             Sai's human label. Answers: "does a checker agree with our
             human on ordinary claims?"
  attack   — adversarially mined pairs from red-team rounds 7 and 8. Gold is
             UNSUPPORTED by construction: each one is a claim whose source
             attributes, denies or hedges it. Answers THE question: "are our
             open classes ordinary-hard or FaithBench-hard?"
  mirror   — the honest twin of each attack, where the source genuinely does
             assert the claim. Gold SUPPORTED.

**The mirrors are not optional.** A checker that answers UNSUPPORTED to
everything scores 100% on the attack set and is worthless. Without the
mirrors this instrument could not detect its own most likely failure — which
is the exact trap three of this project's own instruments fell into.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AA = ROOT / "Agent-Assure"

LONG = ("the Redis cache silently loses acknowledged writes on restart under "
        "default settings")
# Hypotheses must not double the article: f"The {LONG}" yields "The the ...".
CLAIM = LONG[0].upper() + LONG[1:]
SPAN = ("at least three Redis nodes silently lose acknowledged writes on "
        "restart under default settings")

# --- attack pairs: every one verified to reproduce during rounds 7-8 --------
ATTACKS: list[tuple[str, str, str]] = [
    ("R8A-01", f"Critics argued that {LONG}.", f"{CLAIM}."),
    ("R8A-02", f"It is not true that {LONG}.", f"{CLAIM}."),
    ("R8A-01r", f"A blogger speculated that {SPAN}.", f"At least three {SPAN[len('at least three '):]}."),
    ("R8A-02r", f"It is simply not true, whatever the vendor documentation may "
                f"say, that {SPAN}.", f"At least three {SPAN[len('at least three '):]}."),
    ("R8A-03", "Our benchmark showed that the cluster stayed stable. A blogger "
               "speculated that Redis loses data.", "Redis loses data."),
    ("R8A-05a", f"The vendor failed to show that {LONG}.", f"{CLAIM}."),
    ("R8A-05b", f"The team was unable to demonstrate that {LONG}.", f"{CLAIM}."),
    ("R8A-05c", f"Nobody has established that {LONG}.", f"{CLAIM}."),
    ("R8A-05d", f"The auditor declined to confirm that {LONG}.", f"{CLAIM}."),
    ("R8A-07", f"He claimed the {LONG}.", f"{CLAIM}."),
    ("R7-qm1", "The vendor asserts that its inhaler was never recalled in any "
               "regulated market.", "The inhaler was never recalled in any "
               "regulated market."),
    ("R7-qm2", "It is a common misconception that the X200 drone dominates the "
               "commercial mapping market.", "The X200 drone dominates the "
               "commercial mapping market."),
    ("NEG-1", "Redis does not lose acknowledged writes on restart under "
              "default settings.", "Redis loses acknowledged writes on restart "
              "under default settings."),
    ("NEG-2", "The audit found no evidence that the segment margin reached 25 "
              "percent in the fourth quarter.", "The segment margin reached 25 "
              "percent in the fourth quarter."),
    ("REDHERRING-1", "Marketing spend increased twenty percent quarter over "
                     "quarter according to the finance team. Customer signups "
                     "rose sharply in the weeks following the campaign launch.",
                     "Increased marketing spend drives higher customer signups."),
    ("REDHERRING-2", "Median API latency rose noticeably after the last "
                     "infrastructure change. Customer churn increased in the "
                     "same quarter across several segments.",
                     "Higher API latency causes increased customer churn."),
    ("SWAP-1", "Redis sustained 128000 operations per second, twelve times the "
               "throughput of the disk-backed alternative.",
               "The disk-backed alternative sustained 128000 operations per "
               "second, twelve times the throughput of Redis."),
]

# --- mirrors: the honest twin. Gold SUPPORTED. -----------------------------
MIRRORS: list[tuple[str, str, str]] = [
    ("M-factive", f"Our benchmark showed that {LONG}.", f"{CLAIM}."),
    ("M-plain", f"The {LONG}, per our testing.", f"{CLAIM}."),
    ("M-attrib-kept", f"Critics argued that {LONG}.",
                      f"Critics argued that {LONG}."),
    ("M-both", f"Critics argued that {LONG}. Our own benchmark showed that "
               f"{LONG}.", f"{CLAIM}."),
    ("M-paraphrase", "The upgraded rotor motor delivers a longer flight time "
                     "than the previous model in repeated bench testing.",
                     "The upgraded rotor motor provides more flight time than "
                     "the earlier model."),
    ("M-demonstrated", f"Independent testing demonstrated that {SPAN}.",
                       f"At least three {SPAN[len('at least three '):]}."),
    ("M-subset", "Pilot production of the NovaChip process reached a 78% yield "
                 "in the most recent quarter.",
                 "The NovaChip process reached a 78% yield in pilot production."),
    ("M-neg-honest", "Redis does not lose acknowledged writes on restart under "
                     "default settings.",
                     "Redis does not lose acknowledged writes on restart under "
                     "default settings."),
]


def _gold52() -> list[dict]:
    """The 38 entailment-shaped corpus rows, joined to their HUMAN labels."""
    scaffold = {r["claim_id"]: r
                for r in csv.DictReader(
                    (AA / "calibration/labeling-v2.csv").open(encoding="utf-8"))}
    labels = {r["claim_id"]: r
              for r in csv.DictReader(
                  (AA / "calibration/labels-v2.csv").open(encoding="utf-8"))}
    out: list[dict] = []
    for cid, row in scaffold.items():
        if row["source_type"] != "verbatim":
            continue  # absence / unresolved / summary are NOT entailment questions
        human = (labels.get(cid) or {}).get("human_label", "").strip()
        if human not in {"grounded", "violation"}:
            continue
        # evidence is "S1: text ||| S2: text" — strip the id prefixes.
        prem = " ".join(part.split(":", 1)[1].strip()
                        for part in row["evidence"].split("|||")
                        if ":" in part)
        hyp = row["claim_text"]
        for marker in ("[S", "]"):
            pass
        out.append({
            "id": cid, "population": "gold52", "finding": row["query_id"],
            "premise": prem, "hypothesis": hyp,
            "gold": "supported" if human == "grounded" else "unsupported",
        })
    return out


def main() -> None:
    rows: list[dict] = []
    for fid, prem, hyp in ATTACKS:
        rows.append({"id": fid, "population": "attack", "finding": fid,
                     "premise": prem, "hypothesis": hyp,
                     "gold": "unsupported"})
    for fid, prem, hyp in MIRRORS:
        rows.append({"id": fid, "population": "mirror", "finding": fid,
                     "premise": prem, "hypothesis": hyp,
                     "gold": "supported"})
    rows.extend(_gold52())

    out = Path(__file__).parent / "pairs.json"
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    from collections import Counter
    print(f"{len(rows)} pairs -> {out}")
    print(Counter((r["population"], r["gold"]) for r in rows))


if __name__ == "__main__":
    main()
