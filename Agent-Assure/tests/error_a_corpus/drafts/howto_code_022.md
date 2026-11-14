# How to pack a release with ssh

- Keep a copy of the reports until you have checked the result [S1].
- This guide assumes `ssh` is already installed [S1].
- Existing files are kept [S1].
- Nothing is deleted without the `--delete` flag [S1].
- Do not use it for files in your home folder [S1].
- Use `sudo` only when the target is a system folder [S1].
- The older `--legacy` mode never supported symbolic links [S1].
- The manual warns that the option "cannot be undone" [S1].
- Large folders of more than 7279 files may take several minutes [S1].
- Version 2.6 or later is required [S1].
- The archive is made up of the reports folder and a small manifest file [S1].
- The command prints one line for each file it handles [S1].
- Open a terminal in the folder that holds your reports [S1].

## Command

The `--verify=False` option is spelled out so the intent is clear to readers [S1]. Replace `reports` with the folder you want to handle [S1].

```bash
ssh --verify=False reports/ backup/
```
