"""R41 side-by-side differential fuzzer: 6f361f8 (branch) vs ef3ae1f (base), through each module's OWN main().

Usage: uv run python reports/r41_probe/diff_fuzz.py <seed> <n>
Base copy: git show ef3ae1f:Agent-Assure/scripts/ground_check.py > /private/tmp/claude-501/ovn1115-r41/gc_main.py

Calls main() in-process with --json so the CLI wiring (self_source_ids AND the branch's inferred_self_ids) is
exercised exactly. Store/draft files live in a fresh temp dir. Read-only on the repo.

Reports (one JSON line, then examples):
  branch_better  -- gate rank higher, OR score higher, OR any claim GROUNDED/ABSENCE_SUPPORTED on branch and not on base
                    (BLOCKER class; must be 0)
  verdict_diff   -- Counter of (base_verdict -> branch_verdict) for every per-claim difference
  gate_diff / score_diff -- any difference at all
  crash_*        -- a module raised (non-SystemExit)
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import random
import sys
import tempfile
from collections import Counter
from pathlib import Path

AA = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(AA))


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


B = load("gc_branch", str(AA / "scripts" / "ground_check.py"))
M = load("gc_base", "/private/tmp/claude-501/ovn1115-r41/gc_main.py")
GOOD = {"GROUNDED", "ABSENCE_SUPPORTED"}
RANK = {"FAIL": 0, "NEEDS_WORK": 1, "PASS": 2}

TMP = Path(tempfile.mkdtemp(prefix="r41fz-"))
DRAFT = TMP / "draft.md"
STORE = TMP / "store.jsonl"
OTHER = TMP / "other.md"

FIGS = ["25000", "90000", "25,000", "2024", "40 percent", "12%", "3.5 million", "twenty-five thousand", "ninety thousand", ""]
SUBJ = ["The regional bank lost {f} customers in March",
        "Revenue rose to {f} dollars after the audit",
        "The regulator fined Acme {f} euros in June",
        "The survey of {f} staff found widespread fraud",
        "The regional bank collapsed in March after the regulator completed its audit",
        "Acme reported {f} complaints in 2023",
        "No evidence of fraud was found in the {f} audits reviewed",
        "Revenue doubles"]
FILL = ["Staff left.", "Records were filed.", "The board met twice.", "Ok then.", "Officials declined to comment.",
        "The audit took several months to complete."]


def sentence(rng: random.Random, f: str) -> str:
    s = rng.choice(SUBJ)
    return s.format(f=f) if "{f}" in s else s


def build(rng: random.Random):
    """Return (draft_text, records, draft_path_choice)."""
    nsrc = rng.choice([1, 1, 2, 2, 3])
    ids = [f"S{i}" for i in range(1, nsrc + 1)]
    nclaims = rng.choice([1, 1, 2, 3])
    claims = []  # (text_without_marker, cite list, figure)
    for _ in range(nclaims):
        f = rng.choice(FIGS)
        t = sentence(rng, f)
        cites = rng.sample(ids, rng.randint(0, nsrc)) if rng.random() < 0.9 else []
        if not cites and rng.random() < 0.8:
            cites = [rng.choice(ids)]
        claims.append((t, cites, f))
    head = rng.choice(["", "# Findings", "## Results"])
    body = []
    for t, cites, _ in claims:
        mk = "".join(f" [{c}]" for c in cites) if rng.random() < 0.7 else ("" if not cites else " [" + ", ".join(cites) + "]")
        body.append(t + mk + ".")
        if rng.random() < 0.3:
            body.append(rng.choice(FILL))
    sep = rng.choice([" ", "\n\n", "\n"])
    draft = ((head + "\n\n") if head else "") + sep.join(body) + "\n"
    plain = ((head + "\n\n") if head else "") + sep.join(
        t + "." if not t.endswith(".") else t for t, _, _ in claims) + "\n"  # draft without markers
    recs = []
    for sid in ids:
        recs.append(source(rng, sid, claims, plain))
    return draft, recs


def mutate_fig(rng, text, claims):
    for _, _, f in claims:
        if f and f in text and rng.random() < 0.6:
            text = text.replace(f, rng.choice([x for x in FIGS if x and x != f]), 1)
    return text


def source(rng: random.Random, sid: str, claims, plain: str) -> dict:
    kind = rng.choice(["genuine", "genuine_fig", "nearcopy", "nearcopy_fig", "nearcopy_partial", "short_quoted",
                       "path_abs", "path_rel", "path_symlink", "path_hardlink", "hash_meta", "hash_text",
                       "summary", "summary_draft", "failed", "failed_draft", "empty", "partial_contained",
                       "whole_contained", "irrelevant"])
    tool = "mcp__exa__web_fetch_exa"
    fts = "verbatim"
    fp = None
    extent = ""
    status = rng.choice(["", "ok"])
    sha = None
    t0, _, f0 = rng.choice(claims)
    if kind == "genuine":
        text = rng.choice(FILL) + " " + t0 + ". " + rng.choice(FILL)
    elif kind == "genuine_fig":
        text = rng.choice(FILL) + " " + mutate_fig(rng, t0, claims) + ". " + rng.choice(FILL)
    elif kind in ("nearcopy", "nearcopy_fig", "nearcopy_partial"):
        tool = "Read"
        words = plain.split()
        if kind == "nearcopy_partial" and len(words) > 4:
            a = rng.randint(0, len(words) // 2); words = words[a:a + max(3, len(words) // 2)]
        if rng.random() < 0.5 and len(words) > 5:
            words.insert(rng.randint(0, len(words)), rng.choice(["indeed", "reportedly", "also"]))
        text = " ".join(words)
        if kind == "nearcopy_fig":
            text = mutate_fig(rng, text, claims)
        fp = rng.choice([None, str(OTHER)])
        extent = rng.choice(["", "whole", "partial"])
    elif kind == "short_quoted":
        tool = "Read"
        text = mutate_fig(rng, t0, claims) + "." if rng.random() < 0.5 else t0 + "."
        fp = rng.choice([None, str(OTHER)])
        extent = rng.choice(["", "whole", "partial"])
    elif kind.startswith("path_"):
        tool = "Read"
        text = rng.choice([plain, mutate_fig(rng, plain, claims), rng.choice(FILL) + " " + t0 + ". " + rng.choice(FILL)])
        fp = {"path_abs": "@DRAFT", "path_rel": "draft.md", "path_symlink": "@SYMLINK",
              "path_hardlink": "@HARDLINK"}[kind]
        extent = rng.choice(["", "whole"])
    elif kind == "hash_meta":
        text = rng.choice(FILL) + " " + mutate_fig(rng, t0, claims) + ". " + rng.choice(FILL)
        sha = "@DRAFTDIGEST"
    elif kind == "hash_text":
        text = plain if rng.random() < 0.5 else plain.rstrip("\n") + "  "
    elif kind == "summary":
        tool = "WebFetch"; fts = "haiku_summary"
        text = t0 + "."
    elif kind == "summary_draft":
        tool = "WebFetch"; fts = "haiku_summary"
        text = mutate_fig(rng, plain, claims)
    elif kind == "failed":
        status = "failed"
        text = t0 + "."
    elif kind == "failed_draft":
        status = "failed"; tool = "Read"
        text = plain
    elif kind == "empty":
        text = rng.choice(["", " "])
        tool = rng.choice(["Read", "mcp__exa__web_fetch_exa"])
    elif kind == "partial_contained":
        tool = "Read"; extent = rng.choice(["", "partial"])
        text = t0 + "."
    elif kind == "whole_contained":
        tool = "Read"; extent = "whole"
        text = t0 + "."
    else:
        text = "The weather was mild. " + rng.choice(FILL)
    return {"source_id": sid, "url": None if tool == "Read" else f"https://e.com/{sid}", "file_path": fp,
            "fetched_at": "2026-11-15T00:00:00Z", "tool": tool, "content_sha256": sha,
            "text": text, "full_text_source": fts, "captured_via": "inline", "query_provenance": "R41",
            "retrieval_status": status, "read_extent": extent, "_kind": kind}


def materialise(draft: str, recs: list[dict]) -> None:
    DRAFT.write_text(draft, encoding="utf-8")
    OTHER.write_text("unrelated\n", encoding="utf-8")
    for p in (TMP / "link.md", TMP / "hard.md"):
        if p.exists() or p.is_symlink():
            p.unlink()
    os.symlink(DRAFT, TMP / "link.md")
    os.link(DRAFT, TMP / "hard.md")
    digest = B._identity_digest(draft)
    assert digest == M._identity_digest(draft)
    lines = []
    for r in recs:
        o = {k: v for k, v in r.items() if not k.startswith("_")}
        o["file_path"] = {"@DRAFT": str(DRAFT), "@SYMLINK": str(TMP / "link.md"),
                          "@HARDLINK": str(TMP / "hard.md")}.get(o["file_path"], o["file_path"])
        if o["content_sha256"] == "@DRAFTDIGEST":
            o["content_sha256"] = digest
        elif o["content_sha256"] is None:
            o["content_sha256"] = hashlib.sha256(o["text"].encode()).hexdigest()
        lines.append(json.dumps(o, ensure_ascii=False))
    STORE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(mod) -> dict | str:
    argv = sys.argv
    sys.argv = ["ground_check", "--draft", str(DRAFT), "--store", str(STORE), "--json"]
    buf, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            mod.main()
    except SystemExit:
        pass
    except Exception as e:  # noqa: BLE001 -- a crash is a finding, recorded not swallowed
        return f"CRASH:{type(e).__name__}:{str(e)[:80]}"
    finally:
        sys.argv = argv
    out = buf.getvalue()
    if not out:
        return "REFUSED_INPUT:" + err.getvalue().strip()[:80]
    return json.loads(out)


def main() -> None:
    seed, n = int(sys.argv[1]), int(sys.argv[2])
    rng = random.Random(seed)
    c: Counter = Counter()
    vd: Counter = Counter()
    kinds_seen: Counter = Counter()
    ex: dict = {}
    for _ in range(n):
        draft, recs = build(rng)
        materialise(draft, recs)
        for r in recs:
            kinds_seen[r["_kind"]] += 1
        c["multi_source" if len(recs) > 1 else "single_source"] += 1
        rb, rm = run(B), run(M)
        if isinstance(rb, str) or isinstance(rm, str):
            key = ("NONREPORT", rb if isinstance(rb, str) else "report", rm if isinstance(rm, str) else "report")
            c["nonreport_" + ("same" if (isinstance(rb, str) and isinstance(rm, str) and rb.split(":")[0] == rm.split(":")[0]) else "diff")] += 1
            ex.setdefault(key, (draft, recs))
            continue
        c["n"] += 1
        better = RANK[rb["gate"]] > RANK[rm["gate"]] or rb["grounding_score"] > rm["grounding_score"]
        for pb, pm in zip(rb["per_claim"], rm["per_claim"]):
            if pb["verdict"] != pm["verdict"]:
                vd[(pm["verdict"], pb["verdict"])] += 1
            if pb["verdict"] in GOOD and pm["verdict"] not in GOOD:
                better = True
        if len(rb["per_claim"]) != len(rm["per_claim"]):
            c["claimcount_diff"] += 1
        if rb["gate"] != rm["gate"]:
            c["gate_diff"] += 1
        if rb["grounding_score"] != rm["grounding_score"]:
            c["score_diff"] += 1
        if rb["gate"] == "PASS":
            c["branch_pass"] += 1
        if better:
            c["branch_better"] += 1
            ex.setdefault(("BLOCKER", rb["gate"], rm["gate"]), (draft, recs,
                          [p["verdict"] for p in rb["per_claim"]], [p["verdict"] for p in rm["per_claim"]]))
        if any(p["verdict"] == "UNVERIFIED_NUMBER" for p in rb["per_claim"]) and \
                any(p["verdict"] == "UNGROUNDABLE" for p in rm["per_claim"]):
            ex.setdefault(("SAMPLE_UNGROUNDABLE_TO_UNVERIFIED_NUMBER",), (draft, [(r["_kind"], r["text"]) for r in recs]))
    print(json.dumps({"seed": seed, **dict(c), "verdict_diff": {f"{a}->{b}": v for (a, b), v in vd.items()},
                      "kinds": dict(kinds_seen)}))
    for k, v in ex.items():
        print(json.dumps(k), "|", json.dumps(v, default=str)[:700])


if __name__ == "__main__":
    main()
