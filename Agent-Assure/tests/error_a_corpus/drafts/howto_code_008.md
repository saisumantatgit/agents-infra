## Safety checks

1. Check the exit status with `echo $?` after the command ends [S1].
2. The whole procedure takes about 7 minutes [S1].
3. Open a terminal in the folder that holds your reports [S1].
4. The archive is made up of the reports folder and a small manifest file [S1].
5. The default timeout is 7 seconds [S1].

## Command

Add `-n` to keep existing files in place [S1]. Replace `reports` with the folder you want to handle [S1].

```bash
tar -n reports/ backup/
```
