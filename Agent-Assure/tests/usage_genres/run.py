"""Usage-genres instrument: honest drafts in bullet / code / table genres.

Stores are built through the REAL capture hook (Read events), then every draft is
checked with scripts/ground_check.py --json. Run against a FROZEN checkout:

    uv run python tests/usage_genres/run.py --base <frozen checkout>/Agent-Assure

Writes results.json (per-claim verdict + diagnostic) and prints aggregate tables.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SESSION = "usage-genres"


@dataclass(frozen=True)
class ClaimRow:
    draft: str
    genre: str
    variant: str
    text: str
    kind: str
    verdict: str
    diagnostic: str


@dataclass(frozen=True)
class DraftSpec:
    id: str
    genre: str
    variant: str
    sources: tuple[Path, ...]


def load_manifest(base: Path) -> list[DraftSpec]:
    specs = []
    for entry in json.loads((HERE / "manifest.json").read_text()):
        paths = tuple((HERE / s) if s.startswith("sources/") else (base / s)
                      for s in entry["sources"])
        specs.append(DraftSpec(entry["id"], entry["genre"], entry["variant"], paths))
    return specs


def build_store(base: Path, spec: DraftSpec, store: Path) -> None:
    store.unlink(missing_ok=True)
    env = {"ASSURE_EVIDENCE_STORE": str(store), "PATH": "/usr/bin:/bin"}
    for src in spec.sources:
        event = {"tool_name": "Read", "session_id": SESSION, "cwd": str(base),
                 "tool_input": {"file_path": str(src)},
                 "tool_response": {"type": "text", "file": {
                     "filePath": str(src), "content": src.read_text(),
                     "numLines": 1, "startLine": 1, "totalLines": 1}}}
        subprocess.run([sys.executable, str(base / "scripts/capture_hook.py")],
                       input=json.dumps(event), text=True, env=env, check=True,
                       cwd=str(base))


def check(base: Path, draft: Path, store: Path) -> dict:
    out = subprocess.run([sys.executable, str(base / "scripts/ground_check.py"),
                          "--draft", str(draft), "--store", str(store), "--json"],
                         capture_output=True, text=True, cwd=str(base))
    if not out.stdout.strip():
        raise RuntimeError(f"ground_check produced no JSON for {draft}: {out.stderr}")
    return json.loads(out.stdout)


def authored_segments(text: str) -> list[str]:
    """Each cited authored segment (bullet, sentence or table cell), marker removed."""
    segs = []
    for line in text.splitlines():
        line = re.sub(r"^\s*- ", "", line)
        for cell in line.split("|"):
            for part in re.split(r"(?<=\])[.;]?\s+", cell.strip()):
                if re.search(r"\[S\d\]", part):
                    segs.append(re.sub(r"\s*\[S\d\]\.?", "", part).strip(" ."))
    return segs


def authored_spans(text: str) -> list[tuple[int, int]]:
    """Char spans of each authored cited claim (bullet / sentence / table cell)."""
    spans = []
    offset = 0
    for line in text.splitlines(keepends=True):
        cell_off = offset
        for cell in line.split("|"):
            for m in re.finditer(r".*?\[S\d\][.;]?", cell):
                spans.append((cell_off + m.start(), cell_off + m.end()))
            cell_off += len(cell) + 1
        offset += len(line)
    return spans


def authored_verdicts(text: str, segs: list[tuple[str, str]]) -> list[bool]:
    """Per authored claim: True iff every checker segment overlapping it is GROUNDED.

    segs = (segment_text, verdict) in draft order. Raises if a segment cannot be
    located in the draft, so a mismatch is loud, not silently dropped.
    """
    squeezed, origin = [], []
    for i, ch in enumerate(re.sub(r"\[S\d\]", lambda m: " " * len(m.group()), text)):
        if ch.isalnum():
            squeezed.append(ch.lower())
            origin.append(i)
    flat = "".join(squeezed)
    located, cursor = [], 0
    for seg_text, verdict in segs:
        key = "".join(c.lower() for c in re.sub(r"\[S\d\]", "", seg_text) if c.isalnum())
        if not key:
            continue
        pos = flat.find(key, cursor)
        if pos < 0:
            raise RuntimeError(f"segment not locatable in draft: {seg_text!r}")
        located.append((origin[pos], origin[pos + len(key) - 1] + 1, verdict))
        cursor = pos + len(key)
    out = []
    for a, b in authored_spans(text):
        hits = [v for s, e, v in located if s < b and e > a]
        out.append(bool(hits) and all(v == "GROUNDED" for v in hits))
    return out


def copied_is_faithful(text: str, sources: tuple[Path, ...]) -> list[str]:
    corpus = " ".join(" ".join(s.read_text().split()) for s in sources)
    return [s for s in authored_segments(text) if " ".join(s.split()) not in corpus]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--work", type=Path, default=Path("/private/tmp/usage_genres_work"))
    args = ap.parse_args()
    base = args.base.resolve()
    args.work.mkdir(parents=True, exist_ok=True)
    rows: list[ClaimRow] = []
    gates: dict[str, str] = {}
    authored: dict[str, list[bool]] = {}
    unfaithful: dict[str, list[str]] = {}
    for spec in load_manifest(base):
        draft = HERE / "drafts" / f"{spec.id}.md"
        if spec.variant == "copied":
            bad = copied_is_faithful(draft.read_text(), spec.sources)
            if bad:
                unfaithful[spec.id] = bad
        store = args.work / f"{spec.id}.jsonl"
        build_store(base, spec, store)
        report = check(base, draft, store)
        gates[spec.id] = report["gate"]
        authored[spec.id] = authored_verdicts(
            draft.read_text(),
            [(c["text"], c["verdict"]) for c in report["per_claim"]])
        for c in report["per_claim"]:
            rows.append(ClaimRow(spec.id, spec.genre, spec.variant, c["text"],
                                 c["kind"], c["verdict"], c.get("support_diagnostic", "")))
    (HERE / "results.json").write_text(json.dumps(
        {"gates": gates, "authored_grounded": authored, "unfaithful_copied": unfaithful,
         "claims": [asdict(r) for r in rows]}, indent=1) + "\n")
    scored = [r for r in rows if r.kind != "NON_CLAIM"]
    print("copied-draft segments NOT verbatim in source:", unfaithful or "none")
    print("drafts:", len(gates), "PASS:", sum(g == "PASS" for g in gates.values()),
          Counter(gates.values()))
    print("scored claim segments:", len(scored), "GROUNDED:",
          sum(r.verdict == "GROUNDED" for r in scored))
    print("\ngenre | variant | drafts | draft PASS | scored segs | GROUNDED | rate")
    for g in ("bullets", "code", "tables"):
        for v in ("copied", "paraphrased"):
            ds = [s for s, _ in gates.items() if s.split("_")[1] == g and s.split("_")[2] == v]
            sc = [r for r in scored if r.genre == g and r.variant == v]
            ok = sum(r.verdict == "GROUNDED" for r in sc)
            print(f"{g} | {v} | {len(ds)} | {sum(gates[d]=='PASS' for d in ds)} | "
                  f"{len(sc)} | {ok} | {100*ok/max(len(sc),1):.0f}%")
    print("\nAUTHORED claims (bullet/sentence/cell with a citation marker; GROUNDED iff every")
    print("checker segment overlapping it is GROUNDED)")
    print("genre | variant | authored | grounded | rate")
    for g in ("bullets", "code", "tables"):
        for v in ("copied", "paraphrased"):
            flags = [f for d, fl in authored.items()
                     if d.split("_")[1] == g and d.split("_")[2] == v for f in fl]
            print(f"{g} | {v} | {len(flags)} | {sum(flags)} | {100*sum(flags)/max(len(flags),1):.0f}%")
    allf = [f for fl in authored.values() for f in fl]
    print("ALL authored:", len(allf), "grounded:", sum(allf))
    struct = [r for r in scored if "[S" not in r.text]
    print("structural segments scored with no citation (headings, fences, table headers, fragments):",
          len(struct), Counter(r.verdict for r in struct))
    print("\nverdicts of refused:", Counter(r.verdict for r in scored if r.verdict != "GROUNDED"))
    print("refusal reason (verdict, diagnostic):")
    for k, n in Counter((r.verdict, r.diagnostic) for r in scored
                        if r.verdict != "GROUNDED").most_common():
        print(" ", n, k)
    return 0


if __name__ == "__main__":
    sys.exit(main())
