"""Measure v3 with the v1 runner and test-side multi-source/partial captures."""
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('error_b_v1_run', HERE.parent / 'error_b_corpus' / 'run.py')
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)
runner.HERE = HERE
_locate = runner.EA.locate


def locate(text, segs):
    # The checker removes HTML comments before segmenting. Preserve original
    # offsets while applying that same transformation for F5's fake comment.
    text = re.sub(r'<!--.*?-->', lambda m: ' ' * len(m.group()), text, flags=re.S)
    text = text.translate(str.maketrans('⁵⁶⁷', '567'))
    return _locate(text, segs)


runner.EA.locate = locate


def build_store(base, draft_spec, store):
    rows = {r['id']: r for r in json.loads((HERE / 'manifest.json').read_text())}
    row = rows[draft_spec.id]
    paths = [HERE / row['source']]
    if 'source2' in row:
        paths.append(HERE / row['source2'])
    store.unlink(missing_ok=True)
    for path in paths:
        lines = path.read_text().splitlines(keepends=True)
        partial = row.get('partial', False)
        content = ''.join(lines[:2] if partial else lines)
        inp = {'file_path': str(path)}
        if partial:
            inp['limit'] = 2
        event = {'tool_name': 'Read', 'session_id': 'usage-genres', 'cwd': str(base),
                 'tool_input': inp, 'tool_response': {'type': 'text', 'file': {
                     'filePath': str(path), 'content': content, 'numLines': 2 if partial else len(lines),
                     'startLine': 1, 'totalLines': len(lines)}}}
        subprocess.run([sys.executable, str(base / 'scripts/capture_hook.py')],
                       input=json.dumps(event), text=True, check=True, cwd=base,
                       env={'ASSURE_EVIDENCE_STORE': str(store), 'PATH': '/usr/bin:/bin'})

runner.UG.build_store = build_store
if __name__ == '__main__':
    sys.exit(runner.main())
