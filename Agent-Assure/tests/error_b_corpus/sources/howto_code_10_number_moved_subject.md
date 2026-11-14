# How to move a branch with sqlite3

This guide assumes `sqlite3` is already installed. Keep a copy of the photos until you have checked the result. The whole procedure takes about 38 minutes.

The setup script takes 92 minutes to complete. The local server takes 74 minutes to complete.

The same approach works for larger projects. The steps work on Linux and macOS. Paths in the examples are relative to your home folder.

Do not use it for files in your home folder. Use `sudo` only when the target is a system folder. The tool prints a summary when it finishes. It stays silent unless an error occurs or `--verbose` is set.

Large folders of more than 7843 files may take several minutes. The manual warns that the option "cannot be undone". The default timeout is 38 seconds. The archive is made up of the photos folder and a small manifest file. The older `--legacy` mode never supported symbolic links.

Check the exit status with `echo $?` after the command ends. The command prints one line for each file it handles. Each step below can be repeated safely. Open a terminal in the folder that holds your photos.

Screenshots are not needed for this guide. A Windows variant is described at the end of this page. Take a short break between steps if the machine is busy.
