# How to move a branch with sqlite3

- This guide assumes `sqlite3` is already installed [S1].
- Keep a copy of the photos until you have checked the result [S1].
- Do not use it for files in your home folder [S1].
- Use `sudo` only when the target is a system folder [S1].
- The tool prints a summary when it finishes [S1].
- It stays silent unless an error occurs or `--verbose` is set [S1].
- The manual warns that the option "cannot be undone" [S1].
- The default timeout is 38 seconds [S1].
- The archive is made up of the photos folder and a small manifest file [S1].
- The older `--legacy` mode never supported symbolic links [S1].
- Check the exit status with `echo $?` after the command ends [S1].
- The command prints one line for each file it handles [S1].
