# How to back up a folder with sqlite3

- Run the command once to see what it would do [S1].
- Check the exit status with `echo $?` after the command ends [S1].
- Open a terminal in the folder that holds your reports [S1].
- Version 4.1 or later is required [S1].
- Large folders of more than 497 files may take several minutes [S1].
- The manual warns that the option "cannot be undone" [S1].

## Command

Add `-n` to keep existing files in place [S1]. Replace `reports` with the folder you want to handle [S1].

```bash
sqlite3 -n reports/ backup/
```
