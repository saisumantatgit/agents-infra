# Quoting usage instrument — does the tester guide's advice work? (2026-10-25)

**40 drafts (4 batches × 5 drafts × 2 variants), every quotation machine-checked as
an exact substring of its source, stores built through the real capture hook.
Agents' causes are testimony; the causes below were traced by the orchestrator.**

## 1. The guide's original advice FAILS
| Variant | Claims GROUNDED (whole claims) |
|---|---|
| Guide-literal ("The audit found "…" [S1].") | **0** in all four batches |
| Natural quoting | **≤1 per batch** |

**Traced cause (controlled source, orchestrator's own run):** a claim that IS the
source sentence — or its opening 8+ words — GROUNDS, with or without quote marks.
**Any framing** ("The audit found", "The report states that") before the quotation
refuses it, even at 15 quoted words: T1 anchors its 8-token span on the claim's
subject, and the framing is not in the source. The guide's own example failed;
corrected tonight, and its examples are now RUN by `tests/test_guide_examples.py`.

## 2. The corrected advice works — partly
Real source sentences from these stores, copied and cited as the claim:
**prose 21/33 (64%) · bullets 12/35 (34%).**
Remaining refusal shapes: inline code spans; bullet labels with colons; a "no" /
"cannot" inside the sentence (read as an ABSENCE claim); a negation or hedge in the
5 tokens BEFORE the span in the source (look-back window); the splitter cutting at
`;` / `:` / ", and" even inside quotation marks; headings with digits scored as claims.

## 3. Not built tonight, deliberately — for Sai
**Framed quotations** ("The WHO stated that "…"") would let a writer attribute a
quote to anyone: the framing's subject is not checkable against the source, so a
blog's sentence could pass as the WHO's. That is a misattribution Error-B, so it is
a design decision, not a fix.
