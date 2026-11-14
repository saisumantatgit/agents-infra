# How to copy a key with rsync

This guide assumes `rsync` is already installed. Check the exit status with `echo $?` after the command ends. The whole procedure takes about 27 minutes.

The build step takes 76 minutes to complete. The sample project holds 53 entries. The local server handles 40 requests every minute.

A Windows variant is described at the end of this page. Output has been trimmed for readability. Paths in the examples are relative to your home folder.

Run the command from the notes folder. It will not work from a folder without write access. Existing files are kept. Nothing is deleted without the `--delete` flag.

The older `--legacy` mode never supported symbolic links. The manual warns that the option "cannot be undone". The archive is made up of the notes folder and a small manifest file. The default timeout is 27 seconds. Version 1.2 or later is required.

Run the command once to see what it would do. The command prints one line for each file it handles. Each step below can be repeated safely. Open a terminal in the folder that holds your notes.

The steps work on Linux and macOS. The same approach works for larger projects. Further reading is listed at the bottom.

## Command

Add `--no-clobber` to keep existing files in place. Replace `notes` with the folder you want to handle.

```bash
rsync --no-clobber notes/ backup/
```
