# Rebase cheat sheet

- Rebasing replays the commits of the current branch on top of another base commit [S1].
- Each replayed commit receives a new hash, because its parent has changed [S1].
- Conflicts are resolved one commit at a time, and `git rebase --continue` resumes after each fix [S1].
- Rewriting history is unsafe for branches that other people have already pulled [S1].
- A rebase that goes wrong can usually be recovered with `git reflog`, which lists the previous positions of `HEAD` [S1].
