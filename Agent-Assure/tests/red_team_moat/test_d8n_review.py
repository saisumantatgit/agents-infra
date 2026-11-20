"""D8 and R46 numeric regressions; assertions exercise the real gate."""
import pytest
from scripts.ground_check import Claim, ClaimKind, RetrievedSource, Verdict, classify, ground


def src(id, text, path=None, url=None):
    return RetrievedSource(id, url, path, '1970-01-01T00:00:00Z', 'Read', '', text, 'verbatim', 'inline', '')


def check(draft, *sources):
    claim = classify(Claim(0, draft, ClaimKind.FACTUAL, (), ()))
    return ground(claim, {s.source_id: s for s in sources})


def test_cited_denial_refuses():
    c = 'The Alder council approved the annual budget'
    assert check(c + ' [S1][S2].', src('S1', c + '.'), src('S2', c + '. That never happened.')) != Verdict.GROUNDED


@pytest.mark.parametrize('identity', ['path', 'url'])
def test_earlier_capture_cannot_ground(identity):
    c = 'The Alder council approved the annual budget'
    kw = {identity: '/same' if identity == 'path' else 'https://example.com/same'}
    assert check(c + ' [S1].', src('S1', c + '.', **kw), src('S2', 'Correction: no budget was approved.', **kw)) != Verdict.GROUNDED


@pytest.mark.parametrize('source,claim', [
    ('two hundred', 'two'), ('1 200', '200'), ('1\u202f200', '200'),
    ('03/04/2023', '04/03/2023'), ('2023-04-03', '2023-03-04'),
    ('05:30', '30:05'), ('2.10', '2.1'),
])
def test_numeric_refusal(source, claim):
    template = 'The Alder council, following a detailed review of the annual records by staff, recorded {} pilots in the annual training program'
    assert check(template.format(claim) + ' [S1].', src('S1', template.format(source) + '.')) != Verdict.GROUNDED
