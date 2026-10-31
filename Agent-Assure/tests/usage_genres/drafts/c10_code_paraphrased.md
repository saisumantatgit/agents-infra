# Using rebase

`git rebase main` makes the feature branch start from the tip of `main` [S1]. After you fix a conflict, `git rebase --continue` resumes the rebase [S1]. Interactive rebasing with `git rebase -i` allows reordering, squashing, editing and dropping commits [S1]. If a rebase goes wrong, `git reflog` lists the previous positions of `HEAD`, which usually allows a recovery [S1].

```bash
git rebase -i main
```
