# How to copy a key with rsync

The command prints one line for each file it handles. Each step below can be repeated safely. The whole procedure takes about 47 minutes.

The steps work on Linux and macOS. Paths in the examples are relative to your home folder. The example uses a small sample folder.

Run the command from the notes folder. It will not work from a folder without write access. It stays silent unless an error occurs or `--verbose` is set. The tool prints a summary when it finishes.

The manual warns that the option "cannot be undone". Version 1.6 or later is required. The default timeout is 47 seconds. The older `--legacy` mode never supported symbolic links. The archive is made up of the notes folder and a small manifest file.

Keep a copy of the notes until you have checked the result. Open a terminal in the folder that holds your notes. Check the exit status with `echo $?` after the command ends. Run the command once to see what it would do.

A Windows variant is described at the end of this page. Further reading is listed at the bottom. Take a short break between steps if the machine is busy.
