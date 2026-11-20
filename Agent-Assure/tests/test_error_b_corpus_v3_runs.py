"""Guard fixture integrity and real capture behavior without pinning gate verdicts."""
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CORPUS = BASE / 'tests/error_b_corpus_v3'


def test_manifest_and_twins():
    rows = json.loads((CORPUS / 'manifest.json').read_text())
    expected = {*(f'r45_f{i}' for i in range(1, 9)), *(f'r46_n{i}' for i in range(1, 12)), 'r46_d9', 'r46_d8', 'r46_d11', 'r45_e3', *(f'r45_a{i}' for i in range(1, 4)), 'r45_d1', 'r45_d2', *(f'r45_b{i}' for i in range(1, 4)), 'r45_c1', 'r45_e1c', 'r45_g1'}
    assert Counter(r['class'] for r in rows) == {name: 15 for name in expected}
    assert len({r['id'] for r in rows}) == len(rows)
    for row in rows:
        draft = (CORPUS / 'drafts' / f"{row['id']}.md").read_text()
        control = (CORPUS / 'controls' / f"{row['id']}.md").read_text()
        source = (CORPUS / row['source']).read_text()
        start = row['offset']
        assert draft[start:start + len(row['fabricated'])] == row['fabricated']
        assert draft != control
        is_s = row['class'] in {'r46_n3', 'r46_d8', 'r46_d11'} or (row['class'].startswith('r45_') and not row['class'].startswith('r45_f'))
        assert row['class_kind'] == ('S' if is_s else 'T')
        if is_s:
            assert ' '.join(row['fabricated'].casefold().split()) in ' '.join(source.casefold().split())
        if row['class'] == 'r46_d8':
            assert '[S1][S2]' in draft and '[S2]' not in control
            assert 'never happened' in (CORPUS / row['source2']).read_text()
        if row['class'] == 'r46_d11':
            assert row['partial'] and 'never happened' in source.splitlines()[2]
            assert draft.replace(f"{row['fabricated']} [S1].\n", '') == control


def test_corpora_fit_size_budget():
    corpora = [BASE / 'tests' / name for name in ('error_b_corpus', 'error_b_corpus_v2', 'error_b_corpus_v3')]
    size = sum(p.stat().st_size for root in corpora for p in root.rglob('*')
               if p.is_file() and '__pycache__' not in p.parts)
    assert size < 5_000_000


def test_real_captures(tmp_path):
    spec = importlib.util.spec_from_file_location('v3_capture_test', CORPUS / 'run.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = {r['id']: r for r in json.loads((CORPUS / 'manifest.json').read_text())}
    for ident in ('r46_d8_00', 'r46_d11_00'):
        store = tmp_path / f'{ident}.jsonl'
        module.build_store(BASE, module.runner.UG.DraftSpec(ident, 'synthetic', '', ()), store)
        captured = [json.loads(line) for line in store.read_text().splitlines()]
        if ident.startswith('r46_d8'):
            assert [r['source_id'] for r in captured] == ['S1', 'S2']
            assert 'never happened' in captured[1]['text']
        else:
            assert len(captured) == 1 and captured[0]['read_extent'] == 'partial'
            assert rows[ident]['fabricated'] in captured[0]['text']
            assert 'never happened' not in captured[0]['text']


def test_runner_subset(tmp_path):
    out = tmp_path / 'results.json'
    proc = subprocess.run([sys.executable, str(CORPUS / 'run.py'), '--base', str(BASE),
                           '--limit', '34', '--work', str(tmp_path / 'work'), '--out', str(out)],
                          capture_output=True, text=True, cwd=BASE)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(out.read_text())
    assert len(result['drafts']) == 34
    assert all(r['gate'] in {'PASS', 'NEEDS_WORK', 'FAIL'} and r['control_gate'] in {'PASS', 'NEEDS_WORK', 'FAIL'} for r in result['drafts'])
