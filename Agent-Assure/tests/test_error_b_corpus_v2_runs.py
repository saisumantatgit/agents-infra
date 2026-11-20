"""Exercise the v2 measuring instrument without pinning gate outcomes."""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CORPUS = BASE / 'tests' / 'error_b_corpus_v2'
CLASSES = {'direction_flip', 'quantifier_inflation', 'dropped_condition', 'period_shift',
           'comparative_flip', 'scope_widening', 'negation_dropped', 'hedge_dropped'}
NEW = {'denied_after': 'S', 'heading_from_source_words_verbatim': 'S',
       'heading_from_source_words_reassembled': 'T'}


def entries():
    return json.loads((CORPUS / 'manifest.json').read_text())


def test_corpus_and_twins():
    rows = entries()
    assert len({e['id'] for e in rows}) == len(rows)
    assert len({e['genre'] for e in rows}) == 14
    assert set(e['class'] for e in rows) == CLASSES | set(NEW)
    assert all(n >= 15 for n in Counter(e['class'] for e in rows).values())
    assert all(len({e['genre'] for e in rows if e['class'] == c}) == 14 for c in CLASSES)
    for e in rows:
        draft = (CORPUS / 'drafts' / f"{e['id']}.md").read_text()
        control = (CORPUS / 'controls' / f"{e['id']}.md").read_text()
        source = (CORPUS / e['source']).read_text()
        assert draft[e['offset']:e['offset'] + len(e['fabricated'])] == e['fabricated']
        assert draft.count(e['fabricated']) == 1 and e['fabricated'] not in control
        if e['class'] in NEW:
            assert e['class_kind'] == NEW[e['class']]
            assert '## Review notes' in source and '## Review notes' in control
            assert e['fabricated_in_source'] == (e['class_kind'] == 'S')
            if e['class'].startswith('heading_'):
                assert draft == f"## {e['fabricated']} [S1]\n\n" + control
                assert set(e['fabricated'].lower().split()) <= set(source.lower().replace('.', '').split())
            else:
                assert draft.replace(f"{e['fabricated']} [S1].\n\n", '', 1) == control
        else:
            assert ' '.join(e['fabricated'].split()) not in ' '.join(source.split())
            assert draft.replace(e['fabricated'], e['honest'], 1) == control


def test_runner_executes_on_subset(tmp_path):
    out = tmp_path / 'results.json'
    proc = subprocess.run([sys.executable, str(CORPUS / 'run.py'), '--base', str(BASE),
                           '--limit', '8', '--work', str(tmp_path / 'work'), '--out', str(out)],
                          capture_output=True, text=True, cwd=BASE)
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out.read_text())
    assert data['summary']['all']['drafts'] == len(data['drafts']) == len(CLASSES | set(NEW))
    assert all(d['gate'] in {'PASS', 'NEEDS_WORK', 'FAIL'} and isinstance(d['escaped'], bool)
               and d['control_gate'] in {'PASS', 'NEEDS_WORK', 'FAIL'} for d in data['drafts'])
