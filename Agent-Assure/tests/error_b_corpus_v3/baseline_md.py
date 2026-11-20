"""Write the measured v3 baseline; no outcomes are inferred from labels."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
manifest = {e['id']: e for e in json.loads((HERE / 'manifest.json').read_text())}
results = json.loads((HERE / 'results.json').read_text())
rows = results['drafts']
lines = [
    '# Error-B corpus v3 baseline', '',
    'Measured against main `d8c2ec0` (scripts identical to this checkout) with '
    '`Agent-Assure/.venv/bin/python Agent-Assure/tests/error_b_corpus_v3/run.py --base Agent-Assure`. '
    'Synthetic fixtures and labels have not been independently reviewed. '
    'Escaped means every checker segment overlapping the marked fabrication is GROUNDED; '
    'PASS means the entire draft passes. Control PASS is the honest twin.', '',
    'T counts traceability breaks (Error-B); S counts disclosed limitations, refused where detectable. '
    'N3 is S because the shortened claim is an unbroken source run. D8 uses two co-cited sources; '
    'D11 captures the first two lines of a source whose denial follows. '
    'A variant refused by main is retained and counted. Cases do not estimate prevalence.', '',
    'Determinism check: SHA-256 hashes of the manifest and every generated source, draft and control '
    'matched after rebuilding; a second full run produced byte-identical results.json.', '',
    '| Class | Kind | Drafts | Escaped | PASS | Control PASS |',
    '|---|:---:|---:|---:|---:|---:|',
]
for cls, block in results['summary']['by_class'].items():
    kind = next(e['class_kind'] for e in manifest.values() if e['class'] == cls)
    lines.append(f"| {cls} | {kind} | {block['drafts']} | {block['escaped']} | {block['pass']} | {block['control_pass']} |")
lines += ['', '| Kind | Drafts | Escaped | PASS | Control PASS |', '|:---:|---:|---:|---:|---:|']
for kind in ('T', 'S'):
    group = [r for r in rows if manifest[r['id']]['class_kind'] == kind]
    lines.append(f"| {kind} | {len(group)} | {sum(r['escaped'] for r in group)} | {sum(r['gate'] == 'PASS' for r in group)} | {sum(r['control_gate'] == 'PASS' for r in group)} |")
(HERE / 'BASELINE.md').write_text('\n'.join(lines) + '\n')
