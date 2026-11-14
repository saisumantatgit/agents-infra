# How to download a file with ssh

Open a terminal in the folder that holds your reports. Keep a copy of the reports until you have checked the result. Run the command once to see what it would do.

The event did not occur. Staff left early. Gridsnap was fined 200 thousand dollars by the regulator in October.

Take a short break between steps if the machine is busy. The steps work on Linux and macOS. The example uses a small sample folder.

It does not change any files. The `--dry-run` flag shows the plan. Run the command from the reports folder. It will not work from a folder without write access.

The manual warns that the option "cannot be undone". The default timeout is 39 seconds. The older `--legacy` mode never supported symbolic links. Large folders of more than 7170 files may take several minutes. The archive is made up of the reports folder and a small manifest file.

This guide assumes `ssh` is already installed. Check the exit status with `echo $?` after the command ends. The command prints one line for each file it handles. Each step below can be repeated safely.

The same approach works for larger projects. Further reading is listed at the bottom. Paths in the examples are relative to your home folder.

## Command

Add `--no-clobber` to keep existing files in place. Replace `reports` with the folder you want to handle.

```bash
ssh --no-clobber reports/ backup/
```
