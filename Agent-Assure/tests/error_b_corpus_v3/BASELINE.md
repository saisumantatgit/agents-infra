# Error-B corpus v3 baseline

Measured against main `d8c2ec0` (scripts identical to this checkout) with `Agent-Assure/.venv/bin/python Agent-Assure/tests/error_b_corpus_v3/run.py --base Agent-Assure`. Synthetic fixtures and labels have not been independently reviewed. Escaped means every checker segment overlapping the marked fabrication is GROUNDED; PASS means the entire draft passes. Control PASS is the honest twin.

T counts traceability breaks (Error-B); S counts disclosed limitations, refused where detectable. N3 is S because the shortened claim is an unbroken source run. D8 uses two co-cited sources; D11 captures the first two lines of a source whose denial follows. A variant refused by main is retained and counted. Cases do not estimate prevalence.

Determinism check: SHA-256 hashes of the manifest and every generated source, draft and control matched after rebuilding; a second full run produced byte-identical results.json.

| Class | Kind | Drafts | Escaped | PASS | Control PASS |
|---|:---:|---:|---:|---:|---:|
| r45_a1 | S | 15 | 15 | 15 | 15 |
| r45_a2 | S | 15 | 15 | 15 | 15 |
| r45_a3 | S | 15 | 15 | 15 | 15 |
| r45_b1 | S | 15 | 15 | 15 | 15 |
| r45_b2 | S | 15 | 15 | 15 | 15 |
| r45_b3 | S | 15 | 15 | 15 | 15 |
| r45_c1 | S | 15 | 15 | 15 | 15 |
| r45_d1 | S | 15 | 15 | 15 | 15 |
| r45_d2 | S | 15 | 15 | 15 | 15 |
| r45_e1c | S | 15 | 15 | 15 | 15 |
| r45_e3 | S | 15 | 10 | 10 | 15 |
| r45_f1 | T | 15 | 15 | 15 | 15 |
| r45_f2 | T | 15 | 15 | 15 | 15 |
| r45_f3 | T | 15 | 10 | 10 | 15 |
| r45_f4 | T | 15 | 15 | 15 | 15 |
| r45_f5 | T | 15 | 15 | 15 | 15 |
| r45_f6 | T | 15 | 15 | 15 | 15 |
| r45_f7 | T | 15 | 15 | 15 | 15 |
| r45_f8 | T | 15 | 15 | 15 | 15 |
| r45_g1 | S | 15 | 15 | 15 | 15 |
| r46_d11 | S | 15 | 15 | 15 | 15 |
| r46_d8 | S | 15 | 15 | 15 | 15 |
| r46_d9 | T | 15 | 15 | 15 | 15 |
| r46_n1 | T | 15 | 15 | 15 | 15 |
| r46_n10 | T | 15 | 10 | 10 | 15 |
| r46_n11 | T | 15 | 15 | 15 | 15 |
| r46_n2 | T | 15 | 15 | 15 | 15 |
| r46_n3 | S | 15 | 15 | 15 | 15 |
| r46_n4 | T | 15 | 15 | 15 | 15 |
| r46_n5 | T | 15 | 10 | 10 | 15 |
| r46_n6 | T | 15 | 15 | 15 | 15 |
| r46_n7 | T | 15 | 15 | 15 | 15 |
| r46_n8 | T | 15 | 15 | 15 | 15 |
| r46_n9 | T | 15 | 15 | 15 | 15 |

| Kind | Drafts | Escaped | PASS | Control PASS |
|:---:|---:|---:|---:|---:|
| T | 285 | 270 | 270 | 285 |
| S | 225 | 220 | 220 | 225 |
