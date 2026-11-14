"""R37 harness: run (source, draft) cases through branch and main gate CLIs."""
from __future__ import annotations
import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path

AA = Path("/Users/saisumanth/vibe-coding/Agents/ai-overnight-1114/Agent-Assure")
BRANCH = AA / "scripts" / "ground_check.py"
MAIN = Path("/private/tmp/claude-501/r37/gc_main.py")
CLAIM = "The regional bank collapsed in March after the regulator completed its audit"
TAIL = " The regulator published its findings in June."
DRAFT = CLAIM + " [S1].\n"

def run(gate: Path, sources, draft: str):
    with tempfile.TemporaryDirectory(prefix="r37-") as tmp:
        t = Path(tmp)
        lines = []
        for i, text in enumerate(sources, 1):
            lines.append(json.dumps({"source_id": f"S{i}", "url": f"https://example.com/s{i}", "file_path": None,
                "fetched_at": "2026-11-14T00:00:00Z", "tool": "mcp__exa__web_fetch_exa",
                "content_sha256": hashlib.sha256(text.encode()).hexdigest(), "text": text,
                "full_text_source": "verbatim", "captured_via": "inline", "query_provenance": "R37"}, ensure_ascii=False))
        (t / "store.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
        (t / "draft.md").write_text(draft, encoding="utf-8")
        out = subprocess.run([sys.executable, str(gate), "--draft", str(t / "draft.md"), "--store", str(t / "store.jsonl"), "--json"],
                             capture_output=True, text=True, cwd=tmp, env={**os.environ, "PYTHONPATH": str(AA)})
        if not out.stdout:
            return ("CRASH", out.stderr.strip().splitlines()[-1][:120] if out.stderr else "", [])
        r = json.loads(out.stdout)
        v = ["NON_CLAIM" if c["kind"] == "NON_CLAIM" else c["verdict"] for c in r["per_claim"]]
        return (r["gate"], r["grounding_score"], v)

def main(cases_file: str):
    ns: dict = {"CLAIM": CLAIM, "TAIL": TAIL, "DRAFT": DRAFT}
    exec(Path(cases_file).read_text(), ns)
    for name, srcs, draft in ns["CASES"]:
        if isinstance(srcs, str):
            srcs = [srcs]
        b = run(BRANCH, srcs, draft or DRAFT)
        m = run(MAIN, srcs, draft or DRAFT)
        bp = b[0] == "PASS"; mp = m[0] == "PASS"
        flag = "BLOCKER" if bp and not mp else ("HOLE" if bp else ("ERRA?" if mp and not bp else ""))
        print(f"{name:40s} branch={b[0]:10s}{str(b[2]):40s} main={m[0]:10s}{str(m[2]):40s} {flag}")

if __name__ == "__main__":
    main(sys.argv[1])
