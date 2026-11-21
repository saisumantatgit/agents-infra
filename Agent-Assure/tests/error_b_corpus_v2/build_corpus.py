"""Build the synthetic v2 corpus; v1 helpers and Error-A sources remain authoritative."""
from __future__ import annotations
import json
import random
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
V1 = HERE.parent / 'error_b_corpus'
sys.path.insert(0, str(V1))
from build_corpus import A, cited_segments, insert_after_first_paragraph, norm
from fabrications import Ctx, _intro, DENIALS, FILL

CLASSES = ('direction_flip', 'quantifier_inflation', 'dropped_condition', 'period_shift',
           'comparative_flip', 'scope_widening', 'negation_dropped', 'hedge_dropped')


def pair(cls, c, i):
    t, u = c.things_n(2)
    n = c.num()
    val = f'{n}%' if i % 2 else f'{n} percent'
    variants = {
        'direction_flip': [(f'The {t} rose {val} during the review', f'The {t} fell {val} during the review'),
                           (f'The {t} became faster during the review', f'The {t} became slower during the review')],
        'quantifier_inflation': [(f'Some {t} records passed the review', f'All {t} records passed the review'),
                                 (f'Most {t} records passed the review', f'Every {t} record passed the review')],
        'dropped_condition': [(f'Only when the review is complete does the {t} run', f'The {t} runs'),
                              (f'If the review is complete, the {t} runs', f'The {t} runs')],
        'period_shift': [(f'The {t} held {n} entries in 2022', f'The {t} held {n} entries in 2023'),
                         (f'The {t} held {n} entries in the first quarter', f'The {t} held {n} entries in the second quarter')],
        'comparative_flip': [(f'The {t} is larger than the {u}', f'The {u} is larger than the {t}'),
                             (f'The {t} is faster than the {u}', f'The {u} is faster than the {t}')],
        'scope_widening': [(f'The team responsible for the {t} received an audit during the review', f'All teams received an audit during the review'),
                           (f'The team responsible for the {t} received training during the review', f'Every team received training during the review')],
        'negation_dropped': [(f'The {t} does not retain records after the review', f'The {t} retains records after the review'),
                             (f'The {t} never sends records during the review', f'The {t} sends records during the review')],
        'hedge_dropped': [(f'The {t} may retain records after the review', f'The {t} retains records after the review'),
                          (f'The {t} is expected to send records after the review', f'The {t} sends records after the review')],
    }
    return variants[cls][i % 2]


def render(intro, claim, style, position):
    # A full claim in the cited cell retains its subject and scope.
    line = f'{claim} [S1].'
    if style == 1:
        line = '- ' + line
    elif style == 2:
        line = '| Claim |\n|---|\n| ' + line + ' |'
    elif style == 3:
        line = f'{claim}. [S1]'
    return (line + '\n\n' + intro if position == 0 else intro + '\n\n' + line).rstrip() + '\n'


def main():
    entries = json.loads((A / 'manifest.json').read_text())
    genres = sorted({e['genre'] for e in entries})
    assert len(genres) == 14
    for sub in ('drafts', 'controls', 'sources'):
        shutil.rmtree(HERE / sub, ignore_errors=True)
        (HERE / sub).mkdir()
    manifest = []
    for gi, genre in enumerate(genres):
        bases = [e for e in entries if e['genre'] == genre]
        for ci, cls in enumerate(CLASSES):
            for i in range(2):
                e = bases[(ci * 2 + i) % len(bases)]
                source = (A / e['sources'][0]).read_text()
                plain = [x['text'] for x in e['claims'] if x['shape'] == 'plain']
                assert len(plain) >= 2
                c = Ctx(random.Random(1121 + gi * 100 + ci * 2 + i), genre, source, plain)
                honest, fab = pair(cls, c, i)
                full = insert_after_first_paragraph(source, honest + '.')
                style = (gi + ci + i) % 4
                intro = _intro(c)
                draft = render(intro, fab, style, (gi + i) % 2)
                control = render(intro, honest, style, (gi + i) % 2)
                did = f'{genre}_{ci:02d}_{i}_{cls}'
                assert draft.count(fab) == 1 and fab not in control, did
                assert norm(fab) not in norm(full), did
                for seg in cited_segments(draft):
                    assert seg == fab or norm(seg) in norm(full), (did, seg)
                for seg in cited_segments(control):
                    assert norm(seg) in norm(full), (did, seg)
                for folder, text in [('sources', full), ('drafts', draft), ('controls', control)]:
                    (HERE / folder / f'{did}.md').write_text(text)
                manifest.append(dict(id=did, genre=genre, **{'class': cls}, variant=f'form{i}_style{style}',
                                     base=e['id'], source=f'sources/{did}.md', fabricated=fab,
                                     offset=draft.index(fab), honest=honest, fabricated_in_source=False))
    # These cases use a copied section heading even in the honest control. Keep
    # verbatim and reassembled headings separate: ADR-008 classifies them differently.
    denials = [d for d, _ in DENIALS] + [
        'The press made that up.', 'Reporters cooked that up.', 'It was cooked up.']
    for cls in ('denied_after', 'heading_from_source_words_verbatim',
                'heading_from_source_words_reassembled'):
        for i in range(15):
            e = entries[i % len(entries)]
            original = (A / e['sources'][0]).read_text()
            plain = [x['text'] for x in e['claims'] if x['shape'] == 'plain']
            c = Ctx(random.Random(9311 + i), e['genre'], original, plain)
            intro = _intro(c)
            name = f'{["Harbor", "Willow", "Maple", "Cedar", "Birch", "Meadow", "Orchard", "Summit", "Valley", "River", "Linden", "Grove", "Brook", "Forest", "Prairie"][i]} Office'
            claim = (f'The {name} approved the annual budget' if cls == 'denied_after'
                     else f'The regulator found fraud at {name}')
            heading = 'Review notes'
            filler = ' '.join(FILL[:i % 4])
            denial = denials[i]
            full = insert_after_first_paragraph(original, f'## {heading}\n\n{claim}. {filler} {denial}\n\nReview by staff.')
            honest_text = f'## {heading}\n\n{intro}\n'
            if cls == 'denied_after':
                fab = claim
                draft = f'## {heading}\n\n{claim} [S1].\n\n{intro}\n'
                control = honest_text
                kind = 'S'
            else:
                fab = claim if cls.endswith('verbatim') else f'Fraud at {name}'
                # All words in the reassembly occur in the denied sentence.
                draft = f'## {fab} [S1]\n\n{honest_text}'
                control = honest_text
                kind = 'S' if cls.endswith('verbatim') else 'T'
            did = f'{cls}_{i:02d}'
            for folder, text in [('sources', full), ('drafts', draft), ('controls', control)]:
                (HERE / folder / f'{did}.md').write_text(text)
            manifest.append(dict(id=did, genre=e['genre'], **{'class': cls}, variant=f'form{i}',
                                 base=e['id'], source=f'sources/{did}.md', fabricated=fab,
                                 offset=draft.index(fab), honest=None,
                                 fabricated_in_source=kind == 'S', class_kind=kind))
    (HERE / 'manifest.json').write_text(json.dumps(manifest, indent=1) + '\n')
    print(f'{len(manifest)} drafts')

if __name__ == '__main__':
    main()
