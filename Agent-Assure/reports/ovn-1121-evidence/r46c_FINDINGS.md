# R46 lane C: numeric fabrications (written by the main loop from the agent's hand-back; the agent's own write was blocked by the harness)
Root A (N1-N7, N10-N11): past T1's 8-token anchored window, `_anchor_sentence_covers` only checks each claim content word occurs in one source sentence; words may be dropped/reordered and `_STOP_WORDS` (about, after, by, from, more, over, per, than, to, up, in, s) swapped. Root B (N8-N11): `_SOURCE_NUMERIC_RE`/`_parse_numeric_token` read digits + closed suffix list; no space-grouped numbers, ranges, or digit order in dates; 2.10 == 2.1 as float; claim-side `_NUMERIC_RE` lacks `percent`; `spelled_quantity_ok` accepts a sub-run of a spelled number.
N1 bound/approx dropped ("at least 12" -> "12"; "fewer than 5" -> "5", short form too) — evasion W2B-02
N2 preposition comparator swapped ("fell by 10%" -> "fell to 10%"; "by 2027" -> "after 2027")
N3 rate/period dropped ("5 million pounds per month" -> "5 million pounds") — evasion OI-MOAT-01
N4 second denominator ("per user per month, billed once a year" -> "per user per year"; "per user for each team" -> "for each team")
N5 scale/unit dropped or swapped ("40 thousand" -> "40"; "40 ms" -> "40 s"; "30 km per hour" -> "30 per hour")
N6 period/rank dropped ("fiscal 2022" -> "2022"; "Q3 2023" -> "2023"; "third largest" -> "largest")
N7 spelled number truncated ("two hundred" -> "two") — evasion J-43/R12-05
N8 space-grouped thousands split ("1 200" -> "200")
N9 range endpoint as figure ("40-50" -> "50")
N10 digit order in date/time/version (03/04/2023 -> 04/03/2023; 05:30 -> 30:05; 2.10 -> 2.1)
N11 claim "percent" read as a count ("rose by 300 to 1,000, a 43 percent increase" -> "rose by 300 percent")
Fixes: N1-N6 two-way agreement of 2 tokens either side of each matched figure (systemic = W2A-03/J-70 class, Sai); N7 spelled phrase must equal a whole spelled run; N8 parse space groups; N9 range qualifier; N10 compare date/time/version as one string; N11 add percent to _NUMERIC_RE (= C2 ruling).
Main-loop first-hand: 11/11 PASS 100 with own wording and both controls (N4 only in the agent's narrower shapes; plain per-month->per-year refused).
