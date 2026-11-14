# How to move a branch with tar

This guide assumes `tar` is already installed. Open a terminal in the folder that holds your notes. The command prints one line for each file it handles.

Each command is shown in a separate block. The steps work on Linux and macOS. A Windows variant is described at the end of this page.

It does not change any files. The `--dry-run` flag shows the plan. It stays silent unless an error occurs or `--verbose` is set. The tool prints a summary when it finishes.

The archive is made up of the notes folder and a small manifest file. The default timeout is 39 seconds. Version 7.2 or later is required. The older `--legacy` mode never supported symbolic links. The manual warns that the option "cannot be undone".

Keep a copy of the notes until you have checked the result. Run the command once to see what it would do. The whole procedure takes about 39 minutes. Check the exit status with `echo $?` after the command ends.

The same approach works for larger projects. Output has been trimmed for readability. Further reading is listed at the bottom.

## Command

Add `--no-clobber` to keep existing files in place. Replace `notes` with the folder you want to handle.

```bash
tar --no-clobber notes/ backup/
```
