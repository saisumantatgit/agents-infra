"""Score a checker's raw output against gold. Reports per population.

Threshold note: both checkers emit a probability of "supported". We sweep the
threshold rather than assuming 0.5, and report the best achievable numbers —
which is GENEROUS to the checker on purpose. If it fails even at its best
threshold, the failure is real and not a tuning artifact.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

D = Path(__file__).parent


def load(name: str, key: str):
    p = D / f"raw_{name}.json"
    if not p.exists():
        return None, key
    return json.loads(p.read_text()), key


def metrics(rows, key, tau):
    """Positive class = UNSUPPORTED, matching the gate's pinned polarity."""
    tp = fp = tn = fn = 0
    for r in rows:
        pred_unsupported = r[key] < tau
        gold_unsupported = r["gold"] == "unsupported"
        if gold_unsupported and pred_unsupported: tp += 1
        elif gold_unsupported and not pred_unsupported: fn += 1
        elif not gold_unsupported and pred_unsupported: fp += 1
        else: tn += 1
    n = len(rows)
    acc = (tp + tn) / n if n else 0.0
    # balanced accuracy: mean of recall on each class
    rec_u = tp / (tp + fn) if (tp + fn) else float("nan")
    rec_s = tn / (tn + fp) if (tn + fp) else float("nan")
    bal = (rec_u + rec_s) / 2 if (tp + fn) and (tn + fp) else float("nan")
    return {"n": n, "acc": acc, "bal": bal, "miss_unsupported": fn,
            "false_alarm": fp, "tp": tp, "tn": tn}


def main():
    for name, key in (("hhem", "hhem_score"), ("minicheck", "minicheck_score")):
        rows, key = load(name, key)
        if rows is None:
            print(f"\n### {name.upper()} — NOT RUN YET\n")
            continue
        print(f"\n### {name.upper()}  (n={len(rows)})")
        # sweep threshold on the FULL set, pick best balanced accuracy
        taus = sorted({round(r[key], 4) for r in rows} | {0.5})
        best = max(taus, key=lambda t: (metrics(rows, key, t)["bal"] or 0))
        for tau, label in ((0.5, "tau=0.50 (default)"), (best, f"tau={best:.3f} (best)")):
            print(f"\n  {label}")
            print(f"  {'population':<12} {'n':>3} {'acc':>6} {'bal.acc':>8} "
                  f"{'missed unsup':>13} {'false alarms':>13}")
            for pop in ("attack", "mirror", "gold52"):
                sub = [r for r in rows if r["population"] == pop]
                if not sub: continue
                m = metrics(sub, key, tau)
                bal = f"{m['bal']:.3f}" if m["bal"] == m["bal"] else "   n/a"
                print(f"  {pop:<12} {m['n']:>3} {m['acc']:>6.3f} {bal:>8} "
                      f"{m['miss_unsupported']:>13} {m['false_alarm']:>13}")
            m = metrics(rows, key, tau)
            print(f"  {'ALL':<12} {m['n']:>3} {m['acc']:>6.3f} {m['bal']:>8.3f} "
                  f"{m['miss_unsupported']:>13} {m['false_alarm']:>13}")

        print("\n  --- per-attack detail (gold = UNSUPPORTED; low score = caught) ---")
        for r in sorted((x for x in rows if x["population"] == "attack"),
                        key=lambda x: -x[key]):
            flag = "MISS " if r[key] >= 0.5 else "caught"
            print(f"  {flag} {r[key]:.3f}  {r['id']:<14} {r['hypothesis'][:52]}")
        print("\n  --- mirrors (gold = SUPPORTED; high score = correct) ---")
        for r in sorted((x for x in rows if x["population"] == "mirror"),
                        key=lambda x: x[key]):
            flag = "FALSE-ALARM" if r[key] < 0.5 else "ok         "
            print(f"  {flag} {r[key]:.3f}  {r['id']:<14} {r['hypothesis'][:44]}")


if __name__ == "__main__":
    main()
