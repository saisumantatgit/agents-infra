# How to copy a key with rsync

This guide assumes `rsync` is already installed [S1]. Check the exit status with `echo $?` after the command ends [S1]. Run the command from the notes folder [S1]. Existing files are kept [S1].

The older `--legacy` mode never supported symbolic links [S1]. The manual warns that the option "cannot be undone" [S1]. The default timeout is 27 seconds [S1]. Run the command once to see what it would do [S1].

The command prints one line for each file it handles [S1].

## Command

Add `--no-clobber` to keep existing files in place [S1]. Replace `notes` with the folder you want to handle [S1].

```bash
rsync --no-clobber notes/ backup/
```
