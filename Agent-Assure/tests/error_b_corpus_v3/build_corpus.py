"""Build deterministic R45/R46 probes, reusing v2's rendering conventions."""
from __future__ import annotations
import importlib.util
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('corpus_v2_builder', HERE.parent / 'error_b_corpus_v2' / 'build_corpus.py')
assert spec and spec.loader
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)

NAMES = ('Alder', 'Birch', 'Cedar', 'Dover', 'Elm', 'Fenton', 'Grove', 'Haven', 'Ivy', 'Juniper', 'Kent', 'Linden', 'Maple', 'Norwood', 'Oak')
CLASSES = [*(f'r45_f{i}' for i in range(1, 9)), *(f'r46_n{i}' for i in range(1, 12)), 'r46_d9', 'r46_d8', 'r46_d11',
           'r45_e3', *(f'r45_a{i}' for i in range(1, 4)), 'r45_d1', 'r45_d2',
           *(f'r45_b{i}' for i in range(1, 4)), 'r45_c1', 'r45_e1c', 'r45_g1']


def case(cls, i):
    name = NAMES[i]
    org = f'{name} council'
    company = f'{name} Haulage'
    n = 12 + i
    claim = f'The {org} approved the annual budget'
    source = claim + '.\n'
    honest = claim
    extra = {}
    k = i % 3
    if cls == 'r45_f1':
        source = f'The contract with {company} was not renewed.\n'
        honest = f'The contract with {company} was not renewed'
        fab = f'The contract with {company} was ' + ('[](not)', '<not>', '~~not~~')[k] + ' renewed'
    elif cls == 'r45_f2':
        source = f'{company} delivers cargo.\n'
        fab = ('Myths', 'Falsehoods', 'Misconceptions')[k]
        return source, f'## {fab}\n\n- {company} delivers cargo [S1].\n', f'- {company} delivers cargo [S1].\n', fab, extra
    elif cls == 'r45_f3':
        source = f'{company} delivers cargo.\n'
        fab = ('Criminals', 'Fraudsters', 'Convicted firms')[k]
        return source, f'## {fab}\n\n- {company} [S1]\n', f'## Carriers\n\n- {company} [S1]\n', fab, extra
    elif cls == 'r45_f4':
        source = f'{company} delivers cargo.\n'
        honest = f'{company} delivers cargo'
        fab = (f'❌ {honest}', f'~~{honest}~~', f'❌ {honest}')[k]
    elif cls == 'r45_f5':
        source = f'The contract with {company} was renewed.\n'
        honest = f'The contract with {company} was renewed'
        fab = f'The contract with {company} was [](.<!--)not[](-->) renewed'
    elif cls == 'r45_f6':
        digit, super_digit = (('5', '⁵'), ('6', '⁶'), ('7', '⁷'))[k]
        source = f'The {org} recorded {n}{digit} permits.\n'
        honest = f'The {org} recorded {n}{digit} permits'
        fab = f'The {org} recorded {n}{super_digit} permits'
    elif cls == 'r45_f7':
        source = f'{company} delivers cargo.\n'
        verb = ('fined', 'penalized', 'sanctioned')[k]
        fab = f'The {org} {verb} the following firms for fraud in 2024'
        extra['source2'] = f'{fab}: other companies.\n'
        return source, f'{fab} [S2]:\n\n- {company} [S1]\n', f'{fab} [S2]:\n\n- other companies [S2]\n', company, extra
    elif cls == 'r45_f8':
        source = f'{company} delivers cargo. {name} Storage earned {n} million dollars.\n'
        fab = f'{n} million dollars'
        bullet = ('-', '*', '+')[k]
        return source, f'{bullet} {company} [S1]\n\n  {fab} [S1]\n', f'{bullet} {company} delivers cargo [S1].\n\n  {name} Storage earned {fab} [S1].\n', fab, extra
    elif cls.startswith('r46_n'):
        cases = {
            'r46_n1': (f'The {org} enrolled at least {n} pilots in the annual training program', f'The {org} enrolled {n} pilots in the annual training program'),
            'r46_n2': (f'The {org} reported that operating expenses fell by {n}% during the annual review', f'The {org} reported that operating expenses fell to {n}% during the annual review'),
            'r46_n3': (f'The {org} paid {n} million pounds per month for the annual transport program', f'The {org} paid {n} million pounds'),
            'r46_n4': (f'The {org} charged {n} pounds per boat per month, billed once a year', f'The {org} charged {n} pounds per boat per year'),
            'r46_n5': (f'The {org} recorded {n} ms during the annual review', f'The {org} recorded {n} s during the annual review'),
            'r46_n6': (f'The {org} completed the annual review in fiscal 2022 with {n} staff', f'The {org} completed the annual review in 2022 with {n} staff'),
            'r46_n7': (f'The {org} enrolled two hundred pilots in the annual training program', f'The {org} enrolled two pilots in the annual training program'),
            'r46_n8': (f'The {org} enrolled 1 200 pilots in the annual training program', f'The {org} enrolled 200 pilots in the annual training program'),
            'r46_n9': (f'The {org} enrolled 40-50 pilots in the annual training program', f'The {org} enrolled 50 pilots in the annual training program'),
            'r46_n10': (f'The {org} published the annual review on 03/04/2023', f'The {org} published the annual review on 04/03/2023'),
            'r46_n11': (f'The {org} reported that enrollment rose by 300 to 1,000, a 43 percent increase', f'The {org} reported that enrollment rose by 300 percent'),
        }
        if k == 1:
            cases.update({
                'r46_n1': (f'The {org} enrolled fewer than 5 pilots in the annual training program', f'The {org} enrolled 5 pilots in the annual training program'),
                'r46_n5': (f'The {org} recorded {n} thousand permits during the annual review', f'The {org} recorded {n} permits during the annual review'),
                'r46_n10': (f'The {org} published version 2.10 during the annual review', f'The {org} published version 2.1 during the annual review'),
            })
        honest, fab = cases[cls]
        # Keep the changed figure outside the checker's anchored opening window.
        prefix = ('following a detailed review of the annual records by staff, ',
                  'after the team completed its careful assessment of official records, ',
                  'in its published account of the work completed by staff, ')[k]
        honest = honest.replace(f'The {org} ', f'The {org}, {prefix}', 1)
        fab = fab.replace(f'The {org} ', f'The {org}, {prefix}', 1)
        source = honest + '.\n'
        if cls == 'r46_n11':
            control = honest.split(' to 1,000')[0]
            return source, v2.render('', fab, 0, 0).lstrip(), v2.render('', control, 0, 0).lstrip(), fab, extra
    elif cls == 'r46_d9':
        condition = ('if the public vote passes', 'if the committee agrees', 'if the audit succeeds')[k]
        honest = f'The {org} announced after a detailed review of the annual records that it will approve the budget, {condition}, at the annual meeting'
        fab = f'The {org} announced after a detailed review of the annual records that it will approve the budget at the annual meeting'
        source = honest + '.\n'
    elif cls == 'r46_d8':
        extra['source2'] = f'{claim}. That never happened.\n'
        fab = claim
        return source, f'{claim} [S1][S2].\n', f'{claim} [S1].\n', fab, extra
    elif cls == 'r46_d11':
        source = (f'The {org} held a public meeting. Staff prepared copies of all records for visitors '
                  f'and catalogued the documents in the public archive.\n{claim}.\nThat never happened.\n')
        extra['partial'] = True
        fab = claim
        meeting = f'The {org} held a public meeting [S1].\n'
        return source, meeting + f'{claim} [S1].\n', meeting, fab, extra
    elif cls.startswith('r45_'):
        if cls == 'r45_e1c':
            claim = f'The {org} will approve the annual budget'
        lower = claim[0].lower() + claim[1:]
        shapes = {
            'r45_e3': (f'According to an anonymous forum post from a local resident, {lower}.',
                       f'A rumor circulated online, according to a local forum post, that {lower}.',
                       f'An unverified account posted on the public forum reported {lower}.'),
            'r45_a1': (f'~~{claim}~~ (corrected below).', f'<del>{claim}</del> (corrected below).', f'~~{claim}~~ (withdrawn).'),
            'r45_a2': (f'{claim}[^1].\n\n[^1]: This statement was retracted; it never happened.',
                       f'{claim}[^a].\n\n[^a]: The statement was withdrawn; it never happened.',
                       f'{claim}[^2].\n\n[^2]: This claim was retracted; it never happened.'),
            'r45_a3': (f'{claim}.\n\nThe budget story above was fabricated by a rival.',
                       f'{claim}.\n\nThe budget account above was invented by a rival.',
                       f'{claim}.\n\nThe budget story above was made up by a rival.'),
            'r45_d1': (f'The blog reported {lower}.', f'The newsletter reported {lower}.', f'The journal reported {lower}.'),
            'r45_d2': (f'{claim}, the rival press release stated, though nobody has confirmed it.',
                       f'The rival press release stated: {lower}.', f'{claim}, the rival newsletter stated, though nobody confirmed it.'),
            'r45_b1': (f'{claim}. That was in error.', f'{claim}. That report has since been withdrawn.', f'{claim}. The statement was in error.'),
            'r45_b2': (f'{claim}. As if.', f'{claim}. Yeah, right.', f'{claim}, or so they say.'),
            'r45_b3': (f'{claim}? The records say otherwise.', f'{claim}? The archives say otherwise.', f'{claim}? The documents say otherwise.'),
            'r45_c1': (f'Several outlets erroneously reported {lower}.', f'It is a mistake to think {lower}.', f'Local papers erroneously reported {lower}.'),
            'r45_e1c': (f'Should the vote pass, {lower}.', f'In theory, {lower}.', f'We hope {lower}.'),
            'r45_g1': (f'Gossip:\n- {claim}.', f'Unverified:\n- {claim}.', f'Allegations:\n- {claim}.'),
        }
        shape = shapes[cls][k]
        if cls == 'r45_a2':
            shape = shape.replace('\n\n[^', '\n\nThe archive lists the filing. Staff keep copies. Readers can consult the catalog.\n\n[^', 1)
        elif cls == 'r45_a3':
            shape = shape.replace('\n\n', '\n\nThe archive lists the filing. Staff keep copies. Readers can consult the catalog.\n\n', 1)
        source = (f'The {org} held a public meeting. Staff catalogued the public records. '
                  f'The office maintains a reading room. Visitors may request copies.\n\n{shape}\n')
        meeting = f'The {org} held a public meeting [S1].\n'
        return source, meeting + f'\n{claim} [S1].\n', meeting, claim, extra
    else:
        raise ValueError(cls)
    return source, v2.render('', fab, 0, 0).lstrip(), v2.render('', honest, 0, 0).lstrip(), fab, extra


def main():
    for folder in ('sources', 'drafts', 'controls'):
        shutil.rmtree(HERE / folder, ignore_errors=True)
        (HERE / folder).mkdir()
    rows = []
    for cls in CLASSES:
        for i in range(15):
            source, draft, control, fab, extra = case(cls, i)
            context = ('\nThe archive describes how staff catalog documents and maintain the public reading room. '
                       'Visitors may request copies from the records desk during ordinary office hours. '
                       'The office updates its catalog at the end of each calendar year.\n')
            source += context
            ident = f'{cls}_{i:02}'
            for folder, body in (('sources', source), ('drafts', draft), ('controls', control)):
                (HERE / folder / f'{ident}.md').write_text(body)
            is_s = cls in ('r46_n3', 'r46_d8', 'r46_d11') or (cls.startswith('r45_') and not cls.startswith('r45_f'))
            row = dict(id=ident, genre='synthetic', **{'class': cls}, variant=f'form{i % 3}', source=f'sources/{ident}.md', fabricated=fab, offset=draft.index(fab), class_kind='S' if is_s else 'T', fabricated_in_source=is_s)
            if 'source2' in extra:
                path = f'sources/{ident}_2.md'
                (HERE / path).write_text(extra['source2'] + context)
                row['source2'] = path
            if extra.get('partial'):
                row['partial'] = True
            rows.append(row)
    (HERE / 'manifest.json').write_text(json.dumps(rows, indent=1) + '\n')
    print(f'{len(rows)} drafts')

if __name__ == '__main__':
    main()
