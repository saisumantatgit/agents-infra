# How to pack a release with ssh

Check the exit status with `echo $?` after the command ends. Run the command once to see what it would do. Open a terminal in the folder that holds your reports.

Further reading is listed at the bottom.

It will not work from a folder without write access. Run the command from the reports folder. It does not change any files. The `--dry-run` flag shows the plan.

The archive is made up of the reports folder and a small manifest file. The older `--legacy` mode never supported symbolic links. The manual warns that the option "cannot be undone". Large folders of more than 7337 files may take several minutes. The default timeout is 19 seconds.

This guide assumes `ssh` is already installed. The command prints one line for each file it handles. Keep a copy of the reports until you have checked the result. The whole procedure takes about 19 minutes.

Paths in the examples are relative to your home folder.
