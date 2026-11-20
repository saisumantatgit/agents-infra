# How to back up a folder with tar

Keep a copy of the notes until you have checked the result. Each step below can be repeated safely. Check the exit status with `echo $?` after the command ends.

The test runner held 56 entries in 2022.

Output has been trimmed for readability.

The tool prints a summary when it finishes. It stays silent unless an error occurs or `--verbose` is set. It will not work from a folder without write access. Run the command from the notes folder.

The older `--legacy` mode never supported symbolic links. Large folders of more than 8167 files may take several minutes. The default timeout is 30 seconds. The manual warns that the option "cannot be undone". The archive is made up of the notes folder and a small manifest file.

This guide assumes `tar` is already installed. The command prints one line for each file it handles. The whole procedure takes about 30 minutes. Open a terminal in the folder that holds your notes.

Paths in the examples are relative to your home folder.

## Command

Add `-n` to keep existing files in place. Replace `notes` with the folder you want to handle.

```bash
tar -n notes/ backup/
```
