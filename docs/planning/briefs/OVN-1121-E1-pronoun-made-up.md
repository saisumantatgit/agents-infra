# Brief E1: refuse a claim the source denies with a pronoun-subject "made up" (fail-closed)

Executor: Codex (or Claude Opus on Sai's word). One worktree, branch `fix-e1-pronoun-made-up` from main.
Read the repo-root `CLAUDE.md` first; its Conventions and Failure Modes bind. If this spec conflicts with
the repo, STOP and say where. Authority: Sai's AGREED to OVERNIGHT-2026-11-21 C1, "Fix fail-closed only"
(D-119/D-120). Nothing that lets a claim pass that main refuses.

## The hole (reproduced on main d8c2ec0, PASS 100, claim GROUNDED)
Source: "The report is published on Mondays. Quay Trust was acquired by a larger rival last spring.
<DENIAL>" with any of these as <DENIAL>: "That was cooked up by the press." / "It was cooked up." /
"The press made that up." / "Reporters cooked that up." Draft: "Quay Trust was acquired by a larger rival
last spring [S1]." Control: <DENIAL> = "That never happened." → refused today.
Cause (reports/C1-RULING-PACK-2026-11-21.md, E1): R40 reads `_UP_FALSITY_VERBS`
(ground_check.py:3270) only with a content-noun subject ("The story was cooked up"); `cooked` is not in
`_DENIAL_TOKENS` (:3009). A pronoun subject, or "made that up" with the object in between, evades it.

## Do
1. Systemic, not per-phrase: treat "<verb in _UP_FALSITY_VERBS or make/makes/made/making> ... up" as a
   falsity predicate when its subject or object is a pronoun/demonstrative (that, this, it, these, those,
   all of it, the whole thing) as well as a content noun, wherever R40's content-noun reading applies
   (same windows: same sentence, next sentence, paragraph).
2. Keep R36/R38's constituting-sense exemptions ("made up of", "make up two thirds", "make up the
   numbers", "make up the bulk") and prove they hold.
3. Proven-red tests in tests/red_team_moat/: each <DENIAL> above, with 0, 1, 2 fillers between, after and
   before the claim; the forward-pointing sibling "This was made up: <claim>."; honest controls
   "<claim>. It is made up of three parts." and "The team made up the shortfall."
4. Structural guard tests/red_team_moat/test_moat_r42_additive_structure.py: re-pin only if additive, say why.

## Measure (before/after, from Agent-Assure/)
Full suite; tests/error_b_corpus/run.py and tests/error_b_corpus_v2/run.py (no class may rise);
tests/error_a_corpus/run.py (state every honest claim lost, with text); tests/usage_genres/run.py.
Gold labels md5 6215b526d03147295b003d7ccb0d171f unchanged.

## Deliver
Code + tests; reports/E1-PRONOUN-MADE-UP.md (rule, proven-red evidence, numbers, siblings left open,
CEILING comments). Do not push. Final message ≤ 30 lines.
