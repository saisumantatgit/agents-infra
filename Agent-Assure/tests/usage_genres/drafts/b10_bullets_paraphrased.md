# Rebase in a nutshell

- A rebase takes the commits on your branch and applies them again on top of a different base commit [S1].
- Replayed commits get new hashes because their parents are different [S1].
- You deal with conflicts one commit at a time, then continue with `git rebase --continue` [S1].
- The `--abort` option puts the branch back the way it was before the rebase began [S1].
- Rewriting history is unsafe on branches that other people have already pulled [S1].
