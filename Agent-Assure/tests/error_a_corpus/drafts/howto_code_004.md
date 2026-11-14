## Useful flags

- This guide assumes `tar` is already installed [S1].
- Open a terminal in the folder that holds your notes [S1].
- It does not change any files [S1].
- The `--dry-run` flag shows the plan [S1].
- The tool prints a summary when it finishes [S1].
- The archive is made up of the notes folder and a small manifest file [S1].
- The default timeout is 39 seconds [S1].
- Version 7.2 or later is required [S1].
- The older `--legacy` mode never supported symbolic links [S1].
- The manual warns that the option "cannot be undone" [S1].
- Keep a copy of the notes until you have checked the result [S1].
- Run the command once to see what it would do [S1].

## Command

Add `--no-clobber` to keep existing files in place [S1]. Replace `notes` with the folder you want to handle [S1].

```bash
tar --no-clobber notes/ backup/
```
