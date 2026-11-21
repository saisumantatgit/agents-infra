# How to move a branch with tar

The whole procedure takes about 27 minutes. Open a terminal in the folder that holds your notes. Run the command once to see what it would do.

The local server is faster than the build step.

Paths in the examples are relative to your home folder.

Use `sudo` only when the target is a system folder. Do not use it for files in your home folder. The `--dry-run` flag shows the plan. It does not change any files.

The older `--legacy` mode never supported symbolic links. The default timeout is 27 seconds. The archive is made up of the notes folder and a small manifest file. The manual warns that the option "cannot be undone". Version 5.1 or later is required.

Check the exit status with `echo $?` after the command ends. This guide assumes `tar` is already installed. Each step below can be repeated safely. Keep a copy of the notes until you have checked the result.

A Windows variant is described at the end of this page.
