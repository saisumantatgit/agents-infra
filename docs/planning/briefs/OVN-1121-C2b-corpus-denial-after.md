# Brief C2b: fabrication corpus — denial AFTER the claim, and source-word headings (tests only)

Executor: Codex. Branch `corpus-c2b` from main. No file under Agent-Assure/scripts/ changes.
Extend tests/error_b_corpus_v2 (keep v1 byte-identical) with:
1. denied_after: source "<claim>. <0-3 fillers> <DENIAL>." for EVERY phrase in v1 DENIALS plus
   "The press made that up.", "Reporters cooked that up.", "It was cooked up." ≥ 15 drafts, honest twins.
2. heading_from_source_words: draft heading made only of source words that restates a sentence the source
   denies (verbatim copy and reassembly); ≥ 15 drafts; twin = same draft without the heading.
3. Honest controls WITH headings (the v1/v2 controls have none, so heading rules are unmeasured there):
   every control in these two classes carries a source-copied heading.
Regenerate BASELINE.md on main; determinism proof; size < 5 MB. Final message: per-class table.
Expect E1/E2 PASSes on main — that is the point: the corpus must show them before the fixes land.

## Addendum (2026-11-21, after RED-TEAM-R45): add one class per R45 family
Read Agent-Assure/reports/RED-TEAM-R45.md. Add ≥ 15 drafts with honest twins for each of the 22 families
(E1–E3, A1–A3, D1, D2, B1–B3, C1, E1c, G1, F1–F8), varying surface as R45's lanes did (different verbs,
labels, glyphs, list shapes). For F-families the fabrication is in the DRAFT's structure; for the others it
is in the SOURCE's framing. Every class must show its R45 PASSes on main before any fix lands — that is
the instrument's job. Keep total size < 5 MB; split into error_b_corpus_v3/ if v2 would exceed it.
