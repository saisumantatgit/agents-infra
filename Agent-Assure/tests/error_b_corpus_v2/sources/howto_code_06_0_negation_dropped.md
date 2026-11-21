# How to pack a release with rsync

Open a terminal in the folder that holds your notes. Each step below can be repeated safely. Check the exit status with `echo $?` after the command ends.

The test runner does not retain records after the review.

Further reading is listed at the bottom.

Use `sudo` only when the target is a system folder. Do not use it for files in your home folder. It stays silent unless an error occurs or `--verbose` is set. The tool prints a summary when it finishes.

The archive is made up of the notes folder and a small manifest file. The older `--legacy` mode never supported symbolic links. The manual warns that the option "cannot be undone". The default timeout is 45 seconds. Version 7.5 or later is required.

The command prints one line for each file it handles. Run the command once to see what it would do. Keep a copy of the notes until you have checked the result. This guide assumes `rsync` is already installed.

Paths in the examples are relative to your home folder.

## Command

The `--delete=False` option is spelled out so the intent is clear to readers. Replace `notes` with the folder you want to handle.

```bash
rsync --delete=False notes/ backup/
```
