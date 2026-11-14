# How to download a file with tar

Run the command once to see what it would do. Open a terminal in the folder that holds your notes. The command prints one line for each file it handles.

Each command is shown in a separate block.

It does not change any files. The `--dry-run` flag shows the plan. The tool prints a summary when it finishes. It stays silent unless an error occurs or `--verbose` is set.

The archive is made up of the notes folder and a small manifest file. The default timeout is 3 seconds. The older `--legacy` mode never supported symbolic links. The manual warns that the option "cannot be undone". Version 1.4 or later is required.

This guide assumes `tar` is already installed. Each step below can be repeated safely. Check the exit status with `echo $?` after the command ends. The whole procedure takes about 3 minutes.

Take a short break between steps if the machine is busy.
