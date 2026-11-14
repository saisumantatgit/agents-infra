## Safety checks

1. Open a terminal in the folder that holds your reports [S1].
2. Keep a copy of the reports until you have checked the result [S1].
3. The `--dry-run` flag shows the plan [S1].
4. Run the command from the reports folder [S1].
5. The default timeout is 39 seconds [S1].
6. The older `--legacy` mode never supported symbolic links [S1].
7. Large folders of more than 7170 files may take several minutes [S1].
8. The archive is made up of the reports folder and a small manifest file [S1].
9. This guide assumes `ssh` is already installed [S1].
10. Check the exit status with `echo $?` after the command ends [S1].

## Command

Add `--no-clobber` to keep existing files in place [S1]. Replace `reports` with the folder you want to handle [S1].

```bash
ssh --no-clobber reports/ backup/
```
