# How to pack a release with rsync

Open a terminal in the folder that holds your notes [S1]. Each step below can be repeated safely [S1]. Use `sudo` only when the target is a system folder [S1]. Do not use it for files in your home folder [S1].

It stays silent unless an error occurs or `--verbose` is set [S1]. The tool prints a summary when it finishes [S1]. The archive is made up of the notes folder and a small manifest file [S1]. The older `--legacy` mode never supported symbolic links [S1].

The manual warns that the option "cannot be undone" [S1]. The default timeout is 45 seconds [S1]. Version 7.5 or later is required [S1]. The command prints one line for each file it handles [S1].

Run the command once to see what it would do [S1].

## Command

The `--delete=False` option is spelled out so the intent is clear to readers [S1]. Replace `notes` with the folder you want to handle [S1].

```bash
rsync --delete=False notes/ backup/
```
