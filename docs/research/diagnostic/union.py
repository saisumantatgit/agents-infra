"""Does a checker catch what OUR GATE misses? That, not raw accuracy, is the
Swiss-cheese question: a 17% checker is still worth having if its 17% is
disjoint from ours. A 17% checker that catches only what we already catch is
worth nothing.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Agent-Assure" / "scripts"))
import ground_check as g

D = Path(__file__).parent
rows = json.loads((D / "pairs.json").read_text())
hhem = {r["id"]: r["hhem_score"] for r in json.loads((D / "raw_hhem.json").read_text())}
mc_p = D / "raw_minicheck.json"
mc = {r["id"]: r["minicheck_score"] for r in json.loads(mc_p.read_text())} if mc_p.exists() else {}


def gate_verdict(premise: str, hypothesis: str) -> str:
    store = {"S1": g.RetrievedSource(
        source_id="S1", url=None, file_path="/tmp/x",
        fetched_at="2026-09-12T00:00:00Z", tool="Read", content_sha256="s",
        text=premise, full_text_source="verbatim", captured_via="hook",
        query_provenance="q")}
    text = hypothesis.rstrip(".") + " [S1]."
    claims = [g.classify(c) for c in g.decompose(text)]
    rep = g.score_report(claims, store)
    scored = [c for c in rep["per_claim"] if c["kind"] != "NON_CLAIM"]
    return scored[0]["verdict"] if scored else "NON_CLAIM"


def caught(verdict: str) -> bool:
    """Gate 'catches' an unsupported claim iff it does NOT certify it."""
    return verdict not in {"GROUNDED", "ABSENCE_SUPPORTED"}


print(f"{'id':<14} {'gate':<20} {'gate?':<7} {'hhem':<7} {'mc':<7} union")
rowsA = [r for r in rows if r["population"] == "attack"]
g_ok = h_ok = m_ok = u_ok = um_ok = 0
for r in rowsA:
    v = gate_verdict(r["premise"], r["hypothesis"])
    gc = caught(v)
    hc = hhem[r["id"]] < 0.5
    mcs = mc.get(r["id"])
    mcc = (mcs < 0.5) if mcs is not None else None
    g_ok += gc; h_ok += hc; u_ok += (gc or hc)
    if mcc is not None:
        m_ok += mcc; um_ok += (gc or mcc)
    print(f"{r['id']:<14} {v:<20} {'Y' if gc else '.':<7} "
          f"{'Y' if hc else '.':<7} "
          f"{('Y' if mcc else '.') if mcc is not None else '-':<7} "
          f"{'Y' if (gc or hc or bool(mcc)) else '.'}")

n = len(rowsA)
print(f"\nGATE alone      caught {g_ok}/{n}")
print(f"HHEM alone      caught {h_ok}/{n}")
if mc: print(f"MINICHECK alone caught {m_ok}/{n}")
print(f"GATE + HHEM     caught {u_ok}/{n}   (HHEM adds {u_ok - g_ok})")
if mc: print(f"GATE + MINICHECK caught {um_ok}/{n}   (MiniCheck adds {um_ok - g_ok})")

print("\n--- mirrors: does adding a checker cost us false alarms? ---")
for r in [x for x in rows if x["population"] == "mirror"]:
    v = gate_verdict(r["premise"], r["hypothesis"])
    hc = hhem[r["id"]] < 0.5
    print(f"{r['id']:<16} gate={v:<14} hhem_flags={'YES' if hc else 'no'}")
