# LABELS — batch B (red-team history)

CANDIDATE labels by an AI agent — NOT gold; only Sai ratifies gold.

Claims are the gate's own sentence units (it splits some sentences at file extensions, commas in figures and the like). A fragment carries its parent sentence's label; every sentence was checked by hand against its cited source.

| draft | claim | CANDIDATE label | gate verdict | agreement |
|---|---|---|---|---|
| 1 | Round 20 examined the capture layer, namely capture_core.py at 501 lines [S1] | grounded | UNVERIFIED_NUMBER | DISAGREE |
| 1 | capture_hook.py at 197 lines [S1]. | grounded | UNVERIFIED_NUMBER | DISAGREE |
| 1 | It reported six findings, of which three were rated critical, two high and one medium [S1]. | grounded | UNVERIFIED_NUMBER | DISAGREE |
| 1 | The first finding showed that joining MCP content blocks with a newline produces a contiguous span that appears in no single retrieved document [S1]. | grounded | UNVERIFIED_ABSENCE | DISAGREE |
| 1 | In its reproduction the draft claimed that the Zentara inhaler was approved after a full review by the European Medicines Agency [S1] | grounded | UNGROUNDED | DISAGREE |
| 1 | the gate returned PASS with a grounding score of 100.0 [S1]. | grounded | UNGROUNDED | DISAGREE |
| 1 | The report states that it used a hostility instrument only, because no real interactive store was available when it was first written [S1]. | grounded | UNVERIFIED_ABSENCE | DISAGREE |
| 1 | A later amendment records that Sai's live probe session produced a real store of four records [S1]. | grounded | UNGROUNDED | DISAGREE |
| 1 | The lock in assign_and_append held up under 12 concurrent hook processes, which wrote 12 records with 12 distinct ids [S1]. | grounded | UNGROUNDED | DISAGREE |
| 2 | Round 21 attacked the capture fixes C1, C2 and C3 on branch capture-contract-2026-10-10 at HEAD 8f73928 [S2]. | grounded | UNGROUNDED | DISAGREE |
| 2 | It filed seven findings, numbered R21-01 through R21-07 [S2]. | grounded | UNVERIFIED_NUMBER | DISAGREE |
| 2 | Unlike round 20, it had a usage instrument for exa, because the author called the live exa server directly over JSON-RPC [S2] | grounded | UNGROUNDED | DISAGREE |
| 2 | saved the raw responses [S2]. | grounded | UNGROUNDED | DISAGREE |
| 2 | A two-URL fetch of example.com and the IANA page came back as a single content block rather than two [S2]. | grounded | UNGROUNDED | DISAGREE |
| 2 | Since C2 and C3 only engage when a response has at least two blocks, they never run on the real exa server [S2]. | grounded | UNGROUNDED | DISAGREE |
| 2 | A sentence that exists only on iana.org was then certified as source S1, whose recorded origin was example.com, at PASS 100.0 [S2]. | grounded | UNGROUNDED | DISAGREE |
| 2 | The report labels R21-06 as pre-existing, tied to the open items J-35 [S2] | grounded | UNGROUNDED | DISAGREE |
| 2 | J-36, and not as a defect in the new fixes [S2]. | grounded | UNVERIFIED_ABSENCE | DISAGREE |
| 3 | ALPHA-5 was run on 2026-10-10 against build testing-live-2026-10-10 at commit 90e129d, using a depth-1 clone of the branch [S3]. | grounded | UNGROUNDED | DISAGREE |
| 3 | The install.sh script exited 0 [S3] | grounded | UNGROUNDED | DISAGREE |
| 3 | provisioned a fresh .venv [S3]. | grounded | UNGROUNDED | DISAGREE |
| 3 | The fabricated demo draft failed with a score of 50.0 [S3] | grounded | UNGROUNDED | DISAGREE |
| 3 | exit code 1, while the grounded demo draft passed at 100.0 [S3]. | grounded | UNGROUNDED | DISAGREE |
| 3 | The one defect found, A-5-01, is that the snippet printed at the end of install.sh raises a FileNotFoundError for .assure/evidence-store.jsonl [S3]. | grounded | UNGROUNDED | DISAGREE |
| 3 | That file cannot exist in a fresh install, because the store is only written once the PostToolUse hook has fired at least once [S3]. | grounded | UNGROUNDED | DISAGREE |
| 3 | The report rates the severity as low [S3] | grounded | UNGROUNDED | DISAGREE |
| 3 | leaves it unfixed, since install.sh is on the park list as Escalation #4 [S3]. | grounded | UNGROUNDED | DISAGREE |
| 3 | The 16 MB clone was deleted at the end of the run [S3]. | grounded | UNGROUNDED | DISAGREE |
| 4 | The dossier notes that main sits at 009c646 [S4] | grounded | UNGROUNDED | DISAGREE |
| 4 | ships an engine of 1,388 lines, while the branch engine is 4,657 lines [S4]. | grounded | UNGROUNDED | DISAGREE |
| 4 | The merge would bring in 279 commits touching 275 files, with 50,511 lines added [S4] | grounded | UNVERIFIED_NUMBER | DISAGREE |
| 4 | 422 removed, and it deletes no files [S4]. | grounded | UNVERIFIED_ABSENCE | DISAGREE |
| 4 | On the branch tip the suite showed 861 passed, 2 skipped [S4] | grounded | UNGROUNDED | DISAGREE |
| 4 | 68 xfailed, with Error-A at 10/25 (0.400) and Error-B at 0/27 (0.000) [S4]. On one demonstration draft about Zentara seventeen material weaknesses, main returned PASS at 100.0 and the branch returned FAIL at 0.0 [S4]. | grounded | UNGROUNDED | DISAGREE |
| 4 | The author recommends merging, on the asymmetry that leaving main as it is keeps the more dangerous build as the default one [S4]. | grounded | UNGROUNDED | DISAGREE |
| 4 | The dossier says a revert is a single commit with git revert -m 1, because the merge removes no file [S4]. | grounded | UNVERIFIED_ABSENCE | DISAGREE |
| 4 | It also states that the capture-layer items J-35, J-36 [S4] | grounded | UNGROUNDED | DISAGREE |
| 4 | J-38 stay open after the merge [S4]. | grounded | UNGROUNDED | DISAGREE |
| 5 | CR-013 covers the overnight run of 2026-10-10 [S5] | grounded | UNVERIFIED_NUMBER | DISAGREE |
| 5 | cites ratification D-94 [S5]. | grounded | UNGROUNDED | DISAGREE |
| 5 | It reports that the deployed rates are unchanged, with Error-A at 0.400 (10/25) and Error-B at 0.000 (0/27) over n=52 [S5]. | grounded | UNGROUNDED | DISAGREE |
| 5 | The C1 change landed as commit ac77b8e [S5] | grounded | UNGROUNDED | DISAGREE |
| 5 | was proven red on 6 of 7 tests [S5]. | grounded | UNVERIFIED_NUMBER | DISAGREE |
| 5 | Round 21 refuted C2 [S5] | grounded | UNGROUNDED | DISAGREE |
| 5 | C3 on the live tool, the fix landed as 35a180f, and round 22 then found a live partial-failure shape that was fixed in ad9367d [S5]. | grounded | UNGROUNDED | DISAGREE |
| 5 | The stretch item J-97 added one gold row [S5] | grounded | UNGROUNDED | DISAGREE |
| 5 | moved Error-A from 0.400 to 0.440 [S5]. | grounded | UNGROUNDED | DISAGREE |
| 5 | The budget was projected at 2.1M of 3M, with a 3.6M ceiling [S5]. | grounded | UNGROUNDED | DISAGREE |
| 5 | The Error-A price of splitting content blocks stays unmeasured because the corpus has no multi-block capture [S5]. | grounded | UNVERIFIED_ABSENCE | DISAGREE |
