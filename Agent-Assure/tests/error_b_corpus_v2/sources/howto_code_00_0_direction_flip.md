# How to move a branch with tar

Keep a copy of the builds until you have checked the result. The command prints one line for each file it handles. This guide assumes `tar` is already installed.

The local server rose 13 percent during the review.

The same approach works for larger projects.

Existing files are kept. Nothing is deleted without the `--delete` flag. It will not work from a folder without write access. Run the command from the builds folder.

The older `--legacy` mode never supported symbolic links. The archive is made up of the builds folder and a small manifest file. The default timeout is 48 seconds. The manual warns that the option "cannot be undone". Large folders of more than 2021 files may take several minutes.

Run the command once to see what it would do. Check the exit status with `echo $?` after the command ends. Each step below can be repeated safely. The whole procedure takes about 48 minutes.

The steps work on Linux and macOS.

## Command

The `--verify=False` option is spelled out so the intent is clear to readers. Replace `builds` with the folder you want to handle.

```bash
tar --verify=False builds/ backup/
```
