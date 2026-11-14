# How to move a branch with tar

- Keep a copy of the builds until you have checked the result [S1].
- The command prints one line for each file it handles [S1].
- Existing files are kept [S1].
- It will not work from a folder without write access [S1].
- Run the command from the builds folder [S1].
- The older `--legacy` mode never supported symbolic links [S1].
- The archive is made up of the builds folder and a small manifest file [S1].
- The default timeout is 48 seconds [S1].
- The manual warns that the option "cannot be undone" [S1].
- Large folders of more than 2021 files may take several minutes [S1].
- Run the command once to see what it would do [S1].
- Check the exit status with `echo $?` after the command ends [S1].

## Command

The `--verify=False` option is spelled out so the intent is clear to readers [S1]. Replace `builds` with the folder you want to handle [S1].

```bash
tar --verify=False builds/ backup/
```
