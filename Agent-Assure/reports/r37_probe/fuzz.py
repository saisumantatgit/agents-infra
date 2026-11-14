"""R37 differential fuzzer: branch vs main, in-process. Reports branch PASS where main is not PASS."""
from __future__ import annotations
import importlib.util, itertools, json, random, sys, tempfile, hashlib
from pathlib import Path
sys.path.insert(0, "/Users/saisumanth/vibe-coding/Agents/ai-overnight-1114/Agent-Assure")

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m
B = load("gc_branch", "/Users/saisumanth/vibe-coding/Agents/ai-overnight-1114/Agent-Assure/scripts/ground_check.py")
M = load("gc_main", "/private/tmp/claude-501/r37/gc_main.py")

CLAIM = "The regional bank collapsed in March after the regulator completed its audit"
SHORT = "Revenue doubles"
TMP = Path(tempfile.mkdtemp(prefix="r37fz-"))

def store_for(mod, texts):
    p = TMP / (hashlib.sha1(("\x00".join(texts)).encode()).hexdigest() + ".jsonl")
    if not p.exists():
        p.write_text("".join(json.dumps({"source_id": f"S{i}", "url": f"https://e.com/{i}", "file_path": None,
            "fetched_at": "2026-11-14T00:00:00Z", "tool": "mcp__exa__web_fetch_exa",
            "content_sha256": hashlib.sha256(t.encode()).hexdigest(), "text": t, "full_text_source": "verbatim",
            "captured_via": "inline", "query_provenance": "R37"}, ensure_ascii=False) + "\n" for i, t in enumerate(texts, 1)), encoding="utf-8")
    return mod.load_store(str(p))

def gate(mod, texts, draft):
    try:
        claims = [mod.classify(c) for c in mod.decompose(draft)]
        r = mod.score_report(claims, store_for(mod, texts), threshold=90, session_scoped=False, self_source_ids=frozenset())
        return r["gate"], [("NC" if c["kind"] == "NON_CLAIM" else c["verdict"]) for c in r["per_claim"]]
    except Exception as e:
        return "CRASH:" + type(e).__name__ + ":" + str(e)[:60], []

DENIALS = ["None of this is true.", "This never happened.", "The story was fabricated.", "That is made up.",
  "Pure fantasy.", "It is a fairy tale.", "What follows never happened.", "It is false.", "It was concocted.",
  "The account is a myth.", "Made up of rumours.", "The procedure follows the RFC, not the draft.",
  "Not true.", "This did not happen.", "Lies.", "No.", "It is fictional.", "Debunked.", "The board is made up of rumours."]
FILL = ["Staff left.", "Records were filed.", "People talked.", "Ok then."]
HEADINGS = ["", "# Revenue doubles", "## Results", "# Bank Collapses", "# Acme guilty", "## Myths", "## Made up stories",
  "# Revenue doubles [S1]", "# Acme guilty [S1]", "## Fraud everywhere [S1]", "### PostgreSQL Fails [S1]", "## Key findings"]
SRC_HEAD = ["", "## Myths about the bank", "Rumours found to be false", "## Results", "Made up stories"]

def sources(rng):
    d = rng.choice(DENIALS); pre = rng.randint(0, 4); post = rng.randint(0, 2)
    sep = rng.choice([" ", "\n\n", "\n"])
    body = rng.choice([CLAIM, SHORT + " every year", "In the model " + SHORT.lower() + " by 2030", "Acme guilty verdict came in June", "Fraud everywhere was the headline"])
    where = rng.choice(["before", "after", "none", "same"])
    parts = [rng.choice(FILL) for _ in range(pre)]
    if where == "before": parts = [d] + parts
    claim_s = body + (", which is a myth" if where == "same" else "") + "."
    parts = parts + [claim_s] + [rng.choice(FILL) for _ in range(post)]
    if where == "after": parts.append(d)
    text = sep.join(parts)
    h = rng.choice(SRC_HEAD)
    if h: text = h + rng.choice(["\n\n", "\n"]) + text
    return [text]

def drafts(rng):
    h = rng.choice(HEADINGS)
    body = rng.choice([CLAIM + " [S1].", "", SHORT + " [S1].", "Acme guilty [S1].", ""])
    sep = rng.choice(["\n\n", "\n"])
    d = (h + sep if h else "") + body
    return d.strip() + "\n" if d.strip() else "Hello.\n"

rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 37)
N = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
found = {}
counts = {"bothpass": 0, "same": 0, "branch_only_pass": 0, "main_only_pass": 0, "crash": 0}
for _ in range(N):
    s = sources(rng); d = drafts(rng)
    gb, vb = gate(B, s, d); gm, vm = gate(M, s, d)
    if gb.startswith("CRASH") or gm.startswith("CRASH"):
        counts["crash"] += 1; found.setdefault(("CRASH", gb, gm), (s, d)); continue
    if gb == "PASS" and gm != "PASS":
        counts["branch_only_pass"] += 1; found.setdefault(("BLOCKER", tuple(vb), tuple(vm)), (s, d, gb, gm))
    elif gm == "PASS" and gb != "PASS":
        counts["main_only_pass"] += 1
    else:
        counts["same"] += 1
        if gb == "PASS": counts["bothpass"] += 1
print(counts)
for k, v in found.items():
    print(k, json.dumps(v)[:400])
