# Rebase commands

The command `git rebase main` moves the feature branch so that it starts from the tip of `main` [S1]. The option `--abort` restores the branch to the state it had before the rebase began [S1]. The interactive form, `git rebase -i`, lets the author reorder, squash, edit or drop commits [S1].

```bash
git rebase main
git rebase --continue
```
