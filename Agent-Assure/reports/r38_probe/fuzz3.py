"""R38 three-way differential fuzzer: R38 tree vs 2dc776b vs main 83a5cb9, in-process.

Usage: fuzz3.py <seed> <n> [grammar]   grammar = r37 (R37 fuzz.py grammar verbatim) | r38 (adds the
R38 carve-out shapes and their nearest denials). Reports:
  r38_pass_main_refuses   -- gate 1 (must be 0)
  r38_pass_2dc_refuses    -- refusals the R38 narrowing gives back (Error-A restored, or a trade)
Reference copies: /private/tmp/claude-501/r37/gc_main.py (83a5cb9), /private/tmp/claude-501/r38/gc_2dc776b.py."""
from __future__ import annotations
import hashlib, importlib.util, json, random, sys, tempfile
from collections import Counter
from pathlib import Path
AA = "/Users/saisumanth/vibe-coding/Agents/ai-overnight-1114/Agent-Assure"
sys.path.insert(0, AA)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m
R = load("gc_r38", AA + "/scripts/ground_check.py")
B = load("gc_2dc", "/private/tmp/claude-501/r38/gc_2dc776b.py")
M = load("gc_main", "/private/tmp/claude-501/r37/gc_main.py")
TMP = Path(tempfile.mkdtemp(prefix="r38fz-"))
CLAIM = "The regional bank collapsed in March after the regulator completed its audit"
SHORT = "Revenue doubles"

def store_for(mod, texts):
    p = TMP / (hashlib.sha1(("\x00".join(texts)).encode()).hexdigest() + ".jsonl")
    if not p.exists():
        p.write_text("".join(json.dumps({"source_id": f"S{i}", "url": f"https://e.com/{i}", "file_path": None,
            "fetched_at": "2026-11-14T00:00:00Z", "tool": "mcp__exa__web_fetch_exa",
            "content_sha256": hashlib.sha256(t.encode()).hexdigest(), "text": t, "full_text_source": "verbatim",
            "captured_via": "inline", "query_provenance": "R38"}, ensure_ascii=False) + "\n" for i, t in enumerate(texts, 1)), encoding="utf-8")
    return mod.load_store(str(p))

def gate(mod, texts, draft):
    try:
        claims = [mod.classify(c) for c in mod.decompose(draft)]
        r = mod.score_report(claims, store_for(mod, texts), threshold=90, session_scoped=False, self_source_ids=frozenset())
        return r["gate"], tuple(("NC" if c["kind"] == "NON_CLAIM" else c["verdict"]) for c in r["per_claim"])
    except Exception as e:
        return "CRASH:" + type(e).__name__ + ":" + str(e)[:60], ()

R37_DENIALS = ["None of this is true.", "This never happened.", "The story was fabricated.", "That is made up.",
  "Pure fantasy.", "It is a fairy tale.", "What follows never happened.", "It is false.", "It was concocted.",
  "The account is a myth.", "Made up of rumours.", "The procedure follows the RFC, not the draft.",
  "Not true.", "This did not happen.", "Lies.", "No.", "It is fictional.", "Debunked.", "The board is made up of rumours."]
R38_DENIALS = R37_DENIALS + [
  # carve-out shapes (honest) and their nearest denials
  "The board is made up entirely of independent directors.", "The story is made up entirely.",
  "Women made up 40 percent of the workforce.", "The figures were made up.", "It was made up, just like the rest.",
  "The story was made up mostly.", "Made up entirely.", "The panel was made up mostly of economists.",
  "When the strict flag is false, the parser accepts trailing commas.", "The flag is false.", "The report is false.",
  "If the option value is false, logging is disabled.", "The claim is false.", "That is false.",
  "The planned merger never happened.", "The collapse never happened.", "The bank collapse never happened.",
  "That never happened.", "It never happened.", "The events described here never happened.",
  "Prosecutors said the invoices were fabricated.", "Prosecutors said it was fabricated.",
  "Prosecutors said the audit was fabricated.", "Everything here was fabricated.", "The whole thing was invented and fabricated.",
  "Staff ran a fantasy football league.", "The bank story is fantasy.",
  "The procedure follows the RFC, not the draft.", "What follows is not true.", "All that follows is untrue.",
  "Everything that follows is false.", "What now follows did not happen.",
  "This did not affect depositors.", "None of this changed the outcome.", "None of this is accurate.",
  "There is no evidence for any of this.", "None of this can be confirmed.", "This is not real.",
  "We cannot verify any of this.", "None of this happened.", "Not one bit of this is true."]
FILL = ["Staff left.", "Records were filed.", "People talked.", "Ok then."]
R37_HEADINGS = ["", "# Revenue doubles", "## Results", "# Bank Collapses", "# Acme guilty", "## Myths", "## Made up stories",
  "# Revenue doubles [S1]", "# Acme guilty [S1]", "## Fraud everywhere [S1]", "### PostgreSQL Fails [S1]", "## Key findings"]
R38_HEADINGS = R37_HEADINGS + ["## Recent arrests", "## Two raids", "## Boom and bust", "## Everywhere", "## Recent Acme collapses",
  "## Acme recent collapses", "# Bank and doomed", "# Acme doomed", "# Doomed", "## Boom and bust [S1]", "## Recent arrests [S1]",
  "## 3 crashes", "## Acme crashes", "# Slow and doomed", "## Guilty pleas", "## Price rises", "## Bank collapses",
  "## Acme guilty and doomed", "## Imminent: Acme collapse"]
R37_SRC_HEAD = ["", "## Myths about the bank", "Rumours found to be false", "## Results", "Made up stories"]
R38_SRC_HEAD = R37_SRC_HEAD + ["## Myths and facts", "Rumours and facts", "## Fact or fiction", "How the committee is made up",
  "## Myths and facts about the bank", "## Myths, not facts", "Rumours found to be false and the facts", "## Myths vs facts: all false",
  "How the story was made up", "## How it works", "## Fiction", "## Fact and fiction is false", "Myths and facts never happened"]

def sources(rng, D, SH):
    d = rng.choice(D); pre = rng.randint(0, 4); post = rng.randint(0, 2)
    sep = rng.choice([" ", "\n\n", "\n"])
    body = rng.choice([CLAIM, SHORT + " every year", "In the model " + SHORT.lower() + " by 2030", "Acme guilty verdict came in June", "Fraud everywhere was the headline"])
    where = rng.choice(["before", "after", "none", "same"])
    parts = [rng.choice(FILL) for _ in range(pre)]
    if where == "before": parts = [d] + parts
    claim_s = body + (", which is a myth" if where == "same" else "") + "."
    parts = parts + [claim_s] + [rng.choice(FILL) for _ in range(post)]
    if where == "after": parts.append(d)
    text = sep.join(parts)
    h = rng.choice(SH)
    if h: text = h + rng.choice(["\n\n", "\n"]) + text
    return [text], (d if where != "none" else "-", where, h)

def drafts(rng, H):
    h = rng.choice(H)
    body = rng.choice([CLAIM + " [S1].", "", SHORT + " [S1].", "Acme guilty [S1].", ""])
    sep = rng.choice(["\n\n", "\n"])
    d = (h + sep if h else "") + body
    return d.strip() + "\n" if d.strip() else "Hello.\n"

seed = int(sys.argv[1]); n = int(sys.argv[2]); grammar = sys.argv[3] if len(sys.argv) > 3 else "r38"
D, H, SH = (R37_DENIALS, R37_HEADINGS, R37_SRC_HEAD) if grammar == "r37" else (R38_DENIALS, R38_HEADINGS, R38_SRC_HEAD)
rng = random.Random(seed)
c = Counter(); ex: dict = {}; given: Counter = Counter(); gex: dict = {}
for _ in range(n):
    s, meta = sources(rng, D, SH); d = drafts(rng, H)
    gr, vr = gate(R, s, d); gb, vb = gate(B, s, d); gm, vm = gate(M, s, d)
    if any(g.startswith("CRASH") for g in (gr, gb, gm)):
        c["crash"] += 1; ex.setdefault(("CRASH", gr, gb, gm), (s, d)); continue
    c["n"] += 1
    if gr == "PASS": c["r38_pass"] += 1
    if gr == "PASS" and gm != "PASS":
        c["r38_pass_main_refuses"] += 1; ex.setdefault(("BLOCKER", vr, vm), (s, d))
    if gr == "PASS" and gb != "PASS":
        c["r38_pass_2dc_refuses"] += 1; k = (meta[0], meta[1], meta[2], d.strip().replace(chr(10), " / ")); given[k] += 1; gex.setdefault(k, (s[0], vr, vb, vm))
    if gb == "PASS" and gr != "PASS":
        c["2dc_pass_r38_refuses"] += 1; ex.setdefault(("NEW_REFUSAL", vr, vb), (s, d))
print(json.dumps(dict(c)))
for k, v in ex.items():
    print(json.dumps(k)[:220], "|", json.dumps(v)[:400])
print("GIVEN_BACK by (source denial, source heading, draft heading):")
for k, v in given.most_common():
    print(v, json.dumps(k), "||", json.dumps(gex[k]))
