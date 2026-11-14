# How to copy a key with ssh

Run the command once to see what it would do. Each step below can be repeated safely. Open a terminal in the folder that holds your reports.

Further reading is listed at the bottom. Each command is shown in a separate block. The example uses a small sample folder.

The default timeout is 5 seconds. The archive is made up of the reports folder and a small manifest file. Large folders of more than 5409 files may take several minutes.

This guide assumes `ssh` is already installed. The command prints one line for each file it handles. Check the exit status with `echo $?` after the command ends. The whole procedure takes about 5 minutes.

Screenshots are not needed for this guide. Output has been trimmed for readability. A Windows variant is described at the end of this page.

## Command

The `--verify=False` option is spelled out so the intent is clear to readers. Replace `reports` with the folder you want to handle.

```bash
ssh --verify=False reports/ backup/
```
